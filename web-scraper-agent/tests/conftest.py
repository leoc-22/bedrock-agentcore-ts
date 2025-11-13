"""
Shared test fixtures for the Business Web Scraper Agent test suite.
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return path to fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_business_html(fixtures_dir):
    """Load sample business HTML fixture."""
    with open(fixtures_dir / "sample_business.html", "r") as f:
        return f.read()


@pytest.fixture
def minimal_business_html(fixtures_dir):
    """Load minimal business HTML fixture."""
    with open(fixtures_dir / "minimal_business.html", "r") as f:
        return f.read()


@pytest.fixture
def sample_business_url():
    """Sample business website URL."""
    return "https://www.examplebusiness.com.au"


@pytest.fixture
def expected_business_data():
    """Expected extracted data from sample_business.html."""
    return {
        "abn": "51824753556",
        "emails": ["info@examplebusiness.com.au", "support@examplebusiness.com.au"],
        "phones": ["+61 2 9876 5432", "0412 345 678"],
        "addresses": ["123 Business Street, Sydney, NSW 2000"],
        "business_description": "Leading provider of innovative business solutions across Australia. We specialize in enterprise software and consulting services."
    }


@pytest.fixture
def mock_payload():
    """Mock payload for handler testing."""
    return {
        "website": "https://www.example.com.au"
    }


@pytest.fixture
def mock_payload_with_prompt():
    """Mock payload with custom prompt."""
    return {
        "website": "https://www.example.com.au",
        "prompt": "Find the ABN and contact email only."
    }
