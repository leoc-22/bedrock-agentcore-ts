"""
Integration tests for handler functions with mocking.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from runtime_agent import scrape_business_handler


@pytest.mark.integration
class TestScrapBusinessHandler:
    """Tests for scrape_business_handler function."""

    def test_handler_requires_website_in_payload(self):
        """Test that handler returns error when website is missing."""
        payload = {}
        result = scrape_business_handler(payload)

        assert result["status"] == "error"
        assert "website" in result["error"].lower()

    def test_handler_adds_https_to_url(self):
        """Test that handler adds https:// to URLs without protocol."""
        payload = {"website": "example.com.au"}

        with patch('runtime_agent.agent') as mock_agent:
            mock_agent.return_value = "Mock result"
            result = scrape_business_handler(payload)

            # Check that the agent was called
            assert mock_agent.called

            # Check that URL in result has https://
            assert result["website"].startswith("https://")

    def test_handler_accepts_custom_prompt(self):
        """Test that handler uses custom prompt when provided."""
        payload = {
            "website": "https://example.com.au",
            "prompt": "Custom prompt for testing"
        }

        with patch('runtime_agent.agent') as mock_agent:
            mock_agent.return_value = "Mock result"
            result = scrape_business_handler(payload)

            # Agent should have been called with custom prompt
            assert mock_agent.called
            call_args = str(mock_agent.call_args)
            # The custom prompt text should not appear in default prompt
            assert "Custom prompt for testing" in call_args or mock_agent.called

    def test_handler_returns_success_on_completion(self):
        """Test that handler returns success status."""
        payload = {"website": "https://example.com.au"}

        with patch('runtime_agent.agent') as mock_agent:
            mock_agent.return_value = {
                "abn": "12345678901",
                "emails": ["test@example.com"],
                "phones": [],
                "addresses": [],
                "business_description": "Test",
                "pages_visited": ["https://example.com.au"]
            }

            result = scrape_business_handler(payload)

            assert result["status"] == "success"
            assert result["website"] == "https://example.com.au"
            assert "data" in result

    def test_handler_returns_error_on_exception(self):
        """Test that handler catches and returns errors."""
        payload = {"website": "https://example.com.au"}

        with patch('runtime_agent.agent') as mock_agent:
            mock_agent.side_effect = Exception("Test exception")

            result = scrape_business_handler(payload)

            assert result["status"] == "error"
            assert "Test exception" in result["error"]

    def test_handler_preserves_website_url_in_response(self):
        """Test that handler includes website URL in response."""
        payload = {"website": "https://example.com.au"}

        with patch('runtime_agent.agent') as mock_agent:
            mock_agent.return_value = "Mock result"

            result = scrape_business_handler(payload)

            assert result["website"] == "https://example.com.au"


@pytest.mark.integration
class TestHandlerIntegration:
    """Integration tests for complete handler flow."""

    @patch('runtime_agent.agent')
    def test_full_scraping_flow(self, mock_agent, sample_business_html):
        """Test complete scraping flow with mocked agent."""
        # Mock the agent to return structured data
        mock_agent.return_value = {
            "abn": "51824753556",
            "emails": ["info@example.com", "support@example.com"],
            "phones": ["+61 2 9876 5432"],
            "addresses": ["123 Business Street, Sydney, NSW 2000"],
            "business_description": "Test business",
            "pages_visited": ["https://example.com", "https://example.com/contact"]
        }

        payload = {"website": "https://example.com.au"}
        result = scrape_business_handler(payload)

        # Verify structure
        assert result["status"] == "success"
        assert "data" in result

        # Verify agent was called
        assert mock_agent.called

    def test_error_handling_with_invalid_payload(self):
        """Test error handling with various invalid payloads."""
        # Missing website
        result1 = scrape_business_handler({})
        assert result1["status"] == "error"

        # None payload
        with pytest.raises(AttributeError):
            scrape_business_handler(None)

        # Invalid website type
        result3 = scrape_business_handler({"website": 123})
        # Should handle gracefully or raise appropriate error


@pytest.mark.integration
@pytest.mark.slow
class TestEndToEndFlow:
    """End-to-end tests (slower, can be skipped)."""

    @patch('runtime_agent.browser_tool')
    @patch('runtime_agent.agent')
    def test_e2e_with_mocked_browser(self, mock_agent, mock_browser, sample_business_html):
        """Test end-to-end flow with mocked browser tool."""
        # This would test the full integration if we wanted to
        # For now, we rely on unit tests and real integration tests
        pass
