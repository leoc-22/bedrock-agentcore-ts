# Test Suite for Business Web Scraper Agent

This directory contains a comprehensive test suite with both deterministic tests and LLM-as-a-Judge evaluations.

## Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)
Tests individual functions in isolation:
- **`test_extraction.py`**: Tests for HTML parsing and data extraction
- **`test_validation.py`**: Tests for ABN, email, and phone validation

### 2. Integration Tests (`@pytest.mark.integration`)
Tests handler functions with mocked dependencies:
- **`test_handlers.py`**: Tests for `scrape_business_handler` with mocks

### 3. LLM-as-a-Judge Tests (`@pytest.mark.llm_judge`)
Uses an LLM to evaluate agent output quality:
- **`test_llm_judge.py`**: Quality evaluation using Claude Haiku

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests only
pytest -m integration

# LLM judge tests (requires AWS credentials)
pytest -m llm_judge

# Exclude slow tests
pytest -m "not slow"

# Exclude AWS-requiring tests
pytest -m "not requires_aws"
```

### Run Specific Test Files

```bash
# Run extraction tests
pytest tests/test_extraction.py

# Run validation tests
pytest tests/test_validation.py

# Run handler tests
pytest tests/test_handlers.py

# Run LLM judge tests
pytest tests/test_llm_judge.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=. --cov-report=html
```

## Test Markers

Tests are marked with the following markers (defined in `pytest.ini`):

- **`@pytest.mark.unit`**: Fast unit tests
- **`@pytest.mark.integration`**: Integration tests with mocks
- **`@pytest.mark.llm_judge`**: Tests using LLM evaluation
- **`@pytest.mark.slow`**: Slow-running tests
- **`@pytest.mark.requires_aws`**: Tests requiring AWS credentials

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_extraction.py       # Extraction function tests
├── test_validation.py       # Validation function tests
├── test_handlers.py         # Handler integration tests
├── test_llm_judge.py        # LLM-as-a-Judge evaluation
├── fixtures/                # Test data
│   ├── sample_business.html
│   └── minimal_business.html
└── README.md               # This file
```

## LLM-as-a-Judge

The LLM judge evaluates:

1. **Extraction Quality**
   - Completeness: Did we extract all available information?
   - Accuracy: Is the extracted data correct?
   - Format: Are ABN, emails, phones properly formatted?
   - Relevance: Is the description meaningful?

2. **Task Completion**
   - Did the agent understand the task?
   - Were all criteria met?
   - Is the output in the expected format?

### Example LLM Judge Usage

```python
from tests.test_llm_judge import LLMJudge

judge = LLMJudge()

extracted_data = {
    "abn": "51824753556",
    "emails": ["info@example.com"],
    "phones": ["+61 2 9876 5432"],
    "addresses": ["123 Test St, Sydney, NSW 2000"],
    "business_description": "Test business"
}

evaluation = judge.evaluate_extraction_quality(
    extracted_data,
    html_content
)

print(f"Overall Score: {evaluation['overall_score']}/10")
print(f"Feedback: {evaluation['feedback']}")
```

## Writing New Tests

### Unit Test Example

```python
import pytest
from runtime_agent import extract_business_info

@pytest.mark.unit
def test_my_extraction():
    html = "<html><body>ABN: 12 345 678 901</body></html>"
    result = extract_business_info(html, "https://test.com")
    assert result["abn"] == "12345678901"
```

### Integration Test Example

```python
import pytest
from unittest.mock import patch
from runtime_agent import scrape_business_handler

@pytest.mark.integration
def test_my_handler():
    with patch('runtime_agent.agent') as mock_agent:
        mock_agent.return_value = {"abn": "12345678901"}
        result = scrape_business_handler({"website": "https://test.com"})
        assert result["status"] == "success"
```

### LLM Judge Test Example

```python
import pytest
from tests.test_llm_judge import LLMJudge

@pytest.mark.llm_judge
@pytest.mark.requires_aws
def test_my_evaluation(llm_judge):
    data = {"abn": "12345678901"}
    html = "<html>...</html>"

    evaluation = llm_judge.evaluate_extraction_quality(data, html)
    assert evaluation["overall_score"] >= 7
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run unit tests
        run: pytest -m unit
      - name: Run integration tests
        run: pytest -m integration
      - name: Run LLM judge tests
        run: pytest -m llm_judge
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Troubleshooting

### Issue: Tests failing with import errors

**Solution**: Ensure you're running from the project root:
```bash
cd /path/to/web-scraper-agent
pytest
```

### Issue: LLM judge tests skipped

**Solution**: LLM judge tests require AWS credentials:
```bash
aws configure
pytest -m llm_judge
```

### Issue: "No module named 'runtime_agent'"

**Solution**: Install the package in development mode:
```bash
pip install -e .
```

Or add the parent directory to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

## Best Practices

1. **Write tests for new features**: Every new function should have tests
2. **Use fixtures**: Reuse common test data via conftest.py
3. **Mock external dependencies**: Don't hit real APIs in unit tests
4. **Use descriptive names**: Test names should explain what they test
5. **Test edge cases**: Empty inputs, invalid data, errors
6. **Keep tests fast**: Mock slow operations, mark slow tests
7. **Use LLM judge for quality**: Deterministic tests for logic, LLM for quality

## Test Coverage Goals

- **Unit tests**: 80%+ coverage of core functions
- **Integration tests**: All handler functions
- **LLM judge**: Key user journeys and quality metrics

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-mock](https://pytest-mock.readthedocs.io/)
- [Testing Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
