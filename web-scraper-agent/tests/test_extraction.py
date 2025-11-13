"""
Unit tests for business information extraction functions.
"""

import pytest
from runtime_agent import extract_business_info, summarize_business_data


@pytest.mark.unit
class TestExtractBusinessInfo:
    """Tests for extract_business_info function."""

    def test_extract_abn_with_spaces(self, sample_business_html, sample_business_url):
        """Test ABN extraction with spaces."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert result["abn"] == "51824753556"

    def test_extract_abn_without_spaces(self, minimal_business_html):
        """Test ABN extraction without spaces."""
        result = extract_business_info(minimal_business_html, "https://minimal.com.au")

        assert result["abn"] == "12345678901"

    def test_extract_emails(self, sample_business_html, sample_business_url):
        """Test email extraction."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert "info@examplebusiness.com.au" in result["emails"]
        assert "support@examplebusiness.com.au" in result["emails"]
        assert len(result["emails"]) == 2

    def test_extract_phone_numbers(self, sample_business_html, sample_business_url):
        """Test phone number extraction."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert "+61 2 9876 5432" in result["phones"]
        assert "0412 345 678" in result["phones"]

    def test_extract_addresses(self, sample_business_html, sample_business_url):
        """Test address extraction."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert len(result["addresses"]) >= 1
        # Check if address contains key components
        assert any("Sydney" in addr and "NSW" in addr for addr in result["addresses"])

    def test_extract_business_description_from_meta(self, sample_business_html, sample_business_url):
        """Test business description extraction from meta tags."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert result["business_description"] is not None
        assert "business solutions" in result["business_description"].lower()

    def test_extract_url_stored(self, sample_business_html, sample_business_url):
        """Test that URL is stored in result."""
        result = extract_business_info(sample_business_html, sample_business_url)

        assert result["url"] == sample_business_url

    def test_no_abn_returns_none(self):
        """Test that missing ABN returns None."""
        html = "<html><body><p>No ABN here</p></body></html>"
        result = extract_business_info(html, "https://test.com")

        assert result["abn"] is None

    def test_no_emails_returns_empty_list(self):
        """Test that missing emails returns empty list."""
        html = "<html><body><p>No emails here</p></body></html>"
        result = extract_business_info(html, "https://test.com")

        assert result["emails"] == []

    def test_removes_script_and_style_tags(self):
        """Test that script and style tags are removed before processing."""
        html = """
        <html>
            <head><style>.test { color: red; }</style></head>
            <body>
                <script>console.log('test');</script>
                <p>ABN: 12 345 678 901</p>
            </body>
        </html>
        """
        result = extract_business_info(html, "https://test.com")

        # Should extract ABN despite script/style tags
        assert result["abn"] == "12345678901"


@pytest.mark.unit
class TestSummarizeBusinessData:
    """Tests for summarize_business_data function."""

    def test_consolidate_single_page(self):
        """Test consolidation of single page data."""
        data_list = [{
            "url": "https://example.com",
            "abn": "12345678901",
            "emails": ["test@example.com"],
            "phones": ["0400 000 000"],
            "addresses": ["123 Test St, Sydney, NSW 2000"],
            "business_description": "Test business"
        }]

        result = summarize_business_data(data_list)

        assert result["abn"] == "12345678901"
        assert "test@example.com" in result["emails"]
        assert "0400 000 000" in result["phones"]
        assert len(result["pages_visited"]) == 1

    def test_consolidate_multiple_pages(self):
        """Test consolidation of multiple pages."""
        data_list = [
            {
                "url": "https://example.com",
                "abn": "12345678901",
                "emails": ["info@example.com"],
                "phones": ["0400 000 000"],
                "addresses": [],
                "business_description": "Short"
            },
            {
                "url": "https://example.com/contact",
                "abn": None,
                "emails": ["support@example.com"],
                "phones": ["0400 111 111"],
                "addresses": ["123 Test St, Sydney, NSW 2000"],
                "business_description": None
            }
        ]

        result = summarize_business_data(data_list)

        # Should have ABN from first page
        assert result["abn"] == "12345678901"

        # Should have emails from both pages
        assert "info@example.com" in result["emails"]
        assert "support@example.com" in result["emails"]

        # Should have phones from both pages
        assert "0400 000 000" in result["phones"]
        assert "0400 111 111" in result["phones"]

        # Should have address from second page
        assert len(result["addresses"]) == 1

        # Should have 2 pages visited
        assert len(result["pages_visited"]) == 2

    def test_deduplicates_data(self):
        """Test that duplicate data is removed."""
        data_list = [
            {
                "url": "https://example.com/page1",
                "abn": "12345678901",
                "emails": ["test@example.com", "test@example.com"],
                "phones": ["0400 000 000"],
                "addresses": [],
                "business_description": None
            },
            {
                "url": "https://example.com/page2",
                "abn": None,
                "emails": ["test@example.com"],
                "phones": ["0400 000 000"],
                "addresses": [],
                "business_description": None
            }
        ]

        result = summarize_business_data(data_list)

        # Should deduplicate emails
        assert result["emails"].count("test@example.com") == 1

        # Should deduplicate phones
        assert result["phones"].count("0400 000 000") == 1

    def test_keeps_longest_description(self):
        """Test that longest description is kept."""
        data_list = [
            {
                "url": "https://example.com/page1",
                "abn": None,
                "emails": [],
                "phones": [],
                "addresses": [],
                "business_description": "Short"
            },
            {
                "url": "https://example.com/page2",
                "abn": None,
                "emails": [],
                "phones": [],
                "addresses": [],
                "business_description": "This is a much longer description with more details"
            }
        ]

        result = summarize_business_data(data_list)

        assert result["business_description"] == "This is a much longer description with more details"

    def test_first_abn_takes_precedence(self):
        """Test that first ABN found takes precedence."""
        data_list = [
            {
                "url": "https://example.com/page1",
                "abn": "11111111111",
                "emails": [],
                "phones": [],
                "addresses": [],
                "business_description": None
            },
            {
                "url": "https://example.com/page2",
                "abn": "22222222222",
                "emails": [],
                "phones": [],
                "addresses": [],
                "business_description": None
            }
        ]

        result = summarize_business_data(data_list)

        assert result["abn"] == "11111111111"
