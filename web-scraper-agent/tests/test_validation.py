"""
Unit tests for validation tools.
"""

import pytest
from tools.validation import validate_abn, validate_email, validate_australian_phone, format_business_data


@pytest.mark.unit
class TestValidateABN:
    """Tests for ABN validation."""

    def test_valid_abn_with_spaces(self):
        """Test validation of ABN with spaces."""
        assert validate_abn("51 824 753 556") is True

    def test_valid_abn_without_spaces(self):
        """Test validation of ABN without spaces."""
        assert validate_abn("51824753556") is True

    def test_invalid_abn_wrong_checksum(self):
        """Test rejection of ABN with invalid checksum."""
        assert validate_abn("12345678901") is False

    def test_invalid_abn_wrong_length(self):
        """Test rejection of ABN with wrong length."""
        assert validate_abn("123456789") is False
        assert validate_abn("123456789012") is False

    def test_invalid_abn_non_numeric(self):
        """Test rejection of ABN with non-numeric characters."""
        assert validate_abn("ABC12345678") is False

    def test_empty_abn(self):
        """Test rejection of empty ABN."""
        assert validate_abn("") is False

    def test_abn_with_mixed_formatting(self):
        """Test ABN validation with various formatting."""
        # Valid ABN: 51 824 753 556
        assert validate_abn("51-824-753-556") is True
        assert validate_abn("51.824.753.556") is True


@pytest.mark.unit
class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email_simple(self):
        """Test validation of simple email."""
        assert validate_email("test@example.com") is True

    def test_valid_email_with_subdomain(self):
        """Test validation of email with subdomain."""
        assert validate_email("user@mail.example.com.au") is True

    def test_valid_email_with_plus(self):
        """Test validation of email with plus sign."""
        assert validate_email("user+tag@example.com") is True

    def test_valid_email_with_dots(self):
        """Test validation of email with dots."""
        assert validate_email("first.last@example.com") is True

    def test_invalid_email_no_at(self):
        """Test rejection of email without @."""
        assert validate_email("testexample.com") is False

    def test_invalid_email_no_domain(self):
        """Test rejection of email without domain."""
        assert validate_email("test@") is False

    def test_invalid_email_no_local(self):
        """Test rejection of email without local part."""
        assert validate_email("@example.com") is False

    def test_invalid_email_spaces(self):
        """Test rejection of email with spaces."""
        assert validate_email("test @example.com") is False
        assert validate_email("test@ example.com") is False

    def test_empty_email(self):
        """Test rejection of empty email."""
        assert validate_email("") is False


@pytest.mark.unit
class TestValidateAustralianPhone:
    """Tests for Australian phone number validation."""

    def test_valid_phone_international_format(self):
        """Test validation of phone in international format."""
        assert validate_australian_phone("+61 2 9876 5432") is True
        assert validate_australian_phone("+61298765432") is True

    def test_valid_phone_local_format(self):
        """Test validation of phone in local format."""
        assert validate_australian_phone("02 9876 5432") is True
        assert validate_australian_phone("0298765432") is True

    def test_valid_mobile(self):
        """Test validation of mobile number."""
        assert validate_australian_phone("0412 345 678") is True
        assert validate_australian_phone("0412345678") is True

    def test_invalid_phone_wrong_length_international(self):
        """Test rejection of international phone with wrong length."""
        assert validate_australian_phone("+61 2 987 543") is False  # Too short

    def test_invalid_phone_wrong_length_local(self):
        """Test rejection of local phone with wrong length."""
        assert validate_australian_phone("02 987 543") is False  # Too short

    def test_invalid_phone_no_leading_zero(self):
        """Test rejection of phone without leading zero."""
        assert validate_australian_phone("412 345 678") is False

    def test_invalid_phone_non_numeric(self):
        """Test rejection of phone with non-numeric characters."""
        assert validate_australian_phone("04XX XXX XXX") is False

    def test_empty_phone(self):
        """Test rejection of empty phone."""
        assert validate_australian_phone("") is False


@pytest.mark.unit
class TestFormatBusinessData:
    """Tests for business data formatting."""

    def test_format_complete_data(self):
        """Test formatting of complete business data."""
        data = {
            "abn": "51824753556",
            "emails": ["test@example.com"],
            "phones": ["+61 2 9876 5432"],
            "addresses": ["123 Test St, Sydney, NSW 2000"],
            "business_description": "Test business description",
            "pages_visited": ["https://example.com"]
        }

        result = format_business_data(data)

        assert "51824753556" in result
        assert "test@example.com" in result
        assert "+61 2 9876 5432" in result
        assert "123 Test St, Sydney, NSW 2000" in result
        assert "Test business description" in result
        assert "https://example.com" in result

    def test_format_with_validation_markers(self):
        """Test that formatting includes validation status markers."""
        data = {
            "abn": "51824753556",  # Valid ABN
            "emails": ["test@example.com", "invalid-email"],
            "phones": ["+61 2 9876 5432", "123"],
            "addresses": [],
            "business_description": None,
            "pages_visited": []
        }

        result = format_business_data(data)

        # Should show valid ABN
        assert "✓" in result or "Valid" in result

    def test_format_empty_data(self):
        """Test formatting of empty data."""
        data = {
            "abn": None,
            "emails": [],
            "phones": [],
            "addresses": [],
            "business_description": None,
            "pages_visited": []
        }

        result = format_business_data(data)

        # Should still return formatted string (not crash)
        assert isinstance(result, str)
        assert "BUSINESS INFORMATION" in result

    def test_format_partial_data(self):
        """Test formatting of partial data."""
        data = {
            "abn": "51824753556",
            "emails": ["test@example.com"],
            "phones": [],
            "addresses": [],
            "business_description": None,
            "pages_visited": []
        }

        result = format_business_data(data)

        assert "51824753556" in result
        assert "test@example.com" in result
        # Should not crash on missing fields
        assert isinstance(result, str)
