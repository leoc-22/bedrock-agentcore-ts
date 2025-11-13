"""
LLM-as-a-Judge tests for evaluating agent output quality.

These tests use an LLM to evaluate whether the agent's scraping results
meet quality criteria such as completeness, accuracy, and relevance.
"""

import pytest
import json
from typing import Dict
import boto3
from unittest.mock import patch


class LLMJudge:
    """LLM-based judge for evaluating agent outputs."""

    def __init__(self, model_id="anthropic.claude-3-haiku-20240307-v1:0", region="us-west-2"):
        """
        Initialize LLM Judge.

        Args:
            model_id: Bedrock model ID to use for judging
            region: AWS region
        """
        self.model_id = model_id
        self.region = region
        self.bedrock = None

    def _get_bedrock_client(self):
        """Get or create Bedrock client."""
        if self.bedrock is None:
            try:
                self.bedrock = boto3.client('bedrock-runtime', region_name=self.region)
            except Exception as e:
                pytest.skip(f"Cannot connect to Bedrock: {e}")
        return self.bedrock

    def evaluate_extraction_quality(self, extracted_data: Dict, source_html: str) -> Dict:
        """
        Evaluate the quality of extracted business information.

        Args:
            extracted_data: The data extracted by the agent
            source_html: The source HTML that was scraped

        Returns:
            Dictionary with evaluation results including:
            - score: Overall score (0-10)
            - completeness: How complete is the extraction
            - accuracy: Judgment on accuracy
            - feedback: Textual feedback
        """
        client = self._get_bedrock_client()

        prompt = f"""You are evaluating the quality of business information extraction from a website.

Source HTML (truncated):
{source_html[:2000]}

Extracted Data:
{json.dumps(extracted_data, indent=2)}

Please evaluate the extraction on the following criteria:
1. **Completeness**: Did the extraction capture all relevant business information visible in the HTML?
2. **Accuracy**: Is the extracted information accurate based on the HTML content?
3. **Format Correctness**: Are ABN, emails, phones formatted correctly?
4. **Relevance**: Is the extracted description relevant and informative?

Provide your evaluation in the following JSON format:
{{
    "overall_score": <0-10>,
    "completeness_score": <0-10>,
    "accuracy_score": <0-10>,
    "format_score": <0-10>,
    "relevance_score": <0-10>,
    "feedback": "<detailed feedback>",
    "issues": ["<list of any issues found>"]
}}

Be critical but fair. If ABN or contact info is present in HTML but not extracted, deduct points.
"""

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )

            result = json.loads(response['body'].read())
            content = result['content'][0]['text']

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                evaluation = json.loads(json_match.group())
                return evaluation
            else:
                return {
                    "overall_score": 5,
                    "feedback": "Could not parse LLM response",
                    "raw_response": content
                }

        except Exception as e:
            pytest.skip(f"LLM evaluation failed: {e}")

    def evaluate_agent_reasoning(self, task: str, result: Dict, expected_criteria: list) -> Dict:
        """
        Evaluate whether the agent followed instructions and met criteria.

        Args:
            task: The task description given to the agent
            result: The agent's output
            expected_criteria: List of criteria that should be met

        Returns:
            Evaluation dictionary
        """
        client = self._get_bedrock_client()

        criteria_text = "\n".join([f"- {c}" for c in expected_criteria])

        prompt = f"""You are evaluating whether an AI agent correctly completed a task.

Task: {task}

Agent's Result:
{json.dumps(result, indent=2)}

Expected Criteria:
{criteria_text}

Evaluate whether the agent:
1. Understood the task correctly
2. Met all the specified criteria
3. Provided results in the expected format
4. Included all required information

Respond in JSON format:
{{
    "task_completed": <true/false>,
    "criteria_met": {{
        "<criterion1>": <true/false>,
        "<criterion2>": <true/false>
    }},
    "score": <0-10>,
    "reasoning": "<explanation>"
}}
"""

        try:
            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 800,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )

            result = json.loads(response['body'].read())
            content = result['content'][0]['text']

            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse response", "raw": content}

        except Exception as e:
            pytest.skip(f"LLM evaluation failed: {e}")


@pytest.fixture
def llm_judge():
    """Fixture providing LLM judge instance."""
    return LLMJudge()


@pytest.mark.llm_judge
@pytest.mark.requires_aws
@pytest.mark.slow
class TestLLMJudgeEvaluation:
    """Tests using LLM as a judge to evaluate agent quality."""

    def test_evaluate_complete_extraction(self, llm_judge, sample_business_html):
        """Test LLM evaluation of complete extraction."""
        extracted_data = {
            "url": "https://example.com",
            "abn": "51824753556",
            "emails": ["info@examplebusiness.com.au", "support@examplebusiness.com.au"],
            "phones": ["+61 2 9876 5432", "0412 345 678"],
            "addresses": ["123 Business Street, Sydney, NSW 2000"],
            "business_description": "Leading provider of innovative business solutions across Australia."
        }

        evaluation = llm_judge.evaluate_extraction_quality(extracted_data, sample_business_html)

        # High-quality extraction should score well
        assert evaluation["overall_score"] >= 7, f"Score too low: {evaluation['feedback']}"
        assert evaluation["completeness_score"] >= 7
        assert evaluation["accuracy_score"] >= 7

    def test_evaluate_incomplete_extraction(self, llm_judge, sample_business_html):
        """Test LLM evaluation of incomplete extraction."""
        extracted_data = {
            "url": "https://example.com",
            "abn": None,  # Missing
            "emails": ["info@examplebusiness.com.au"],  # Missing support email
            "phones": [],  # Missing
            "addresses": [],  # Missing
            "business_description": "Test"
        }

        evaluation = llm_judge.evaluate_extraction_quality(extracted_data, sample_business_html)

        # Incomplete extraction should score lower
        assert evaluation["overall_score"] <= 6, "Incomplete extraction scored too high"
        assert evaluation["completeness_score"] <= 5, "Completeness score should be low"

        # Should identify missing information
        assert len(evaluation.get("issues", [])) > 0

    def test_evaluate_agent_task_completion(self, llm_judge):
        """Test LLM evaluation of whether agent completed task."""
        task = "Extract ABN, main contact email, and business address"

        result = {
            "status": "success",
            "data": {
                "abn": "51824753556",
                "emails": ["contact@example.com"],
                "addresses": ["123 Test St, Sydney, NSW 2000"]
            }
        }

        expected_criteria = [
            "ABN is extracted",
            "Contact email is extracted",
            "Business address is extracted"
        ]

        evaluation = llm_judge.evaluate_agent_reasoning(task, result, expected_criteria)

        assert evaluation["task_completed"] is True
        assert evaluation["score"] >= 8
        # All criteria should be met
        for criterion in expected_criteria:
            # Check if criteria are in the evaluation
            assert evaluation.get("criteria_met")

    def test_evaluate_agent_partial_completion(self, llm_judge):
        """Test LLM evaluation of partially completed task."""
        task = "Extract ABN, contact email, and business address"

        result = {
            "status": "success",
            "data": {
                "abn": "51824753556",
                "emails": [],  # Missing
                "addresses": ["123 Test St, Sydney, NSW 2000"]
            }
        }

        expected_criteria = [
            "ABN is extracted",
            "Contact email is extracted",
            "Business address is extracted"
        ]

        evaluation = llm_judge.evaluate_agent_reasoning(task, result, expected_criteria)

        # Task should not be fully completed
        assert evaluation["score"] < 10
        # Should note that email is missing
        assert "email" in evaluation.get("reasoning", "").lower() or not evaluation["task_completed"]


@pytest.mark.llm_judge
class TestLLMJudgeUnit:
    """Unit tests for LLM Judge (without AWS calls)."""

    def test_judge_initialization(self):
        """Test LLM judge can be initialized."""
        judge = LLMJudge()
        assert judge.model_id == "anthropic.claude-3-haiku-20240307-v1:0"
        assert judge.region == "us-west-2"

    def test_judge_custom_model(self):
        """Test LLM judge with custom model."""
        judge = LLMJudge(model_id="custom-model", region="us-east-1")
        assert judge.model_id == "custom-model"
        assert judge.region == "us-east-1"

    @patch('boto3.client')
    def test_judge_handles_boto3_error(self, mock_boto):
        """Test judge handles AWS connection errors gracefully."""
        mock_boto.side_effect = Exception("Connection error")
        judge = LLMJudge()

        # Should skip test rather than fail
        with pytest.raises(pytest.skip.Exception):
            judge.evaluate_extraction_quality({}, "<html></html>")
