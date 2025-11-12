#!/usr/bin/env python3
"""
Business Web Scraper Agent - AgentCore Runtime Deployment Version

This version uses BedrockAgentCoreApp with @entrypoint decorator for deployment
to AWS Bedrock AgentCore Runtime as a managed, scalable service.

Deploy using the bedrock-agentcore-starter-toolkit:
    agentcore configure
    agentcore launch --entrypoint runtime_agent.py
    agentcore invoke --payload '{"website": "https://example.com.au"}'
"""

import json
import re
from typing import Dict, List
from strands import Agent, tool
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore import BedrockAgentCoreApp

# Initialize the AgentCore app
app = BedrockAgentCoreApp()


@tool
def extract_business_info(html_content: str, page_url: str) -> Dict[str, any]:
    """
    Extract business information from HTML content.

    This tool analyzes HTML content and extracts:
    - ABN (Australian Business Number)
    - Email addresses
    - Phone numbers
    - Physical addresses
    - Business description

    Args:
        html_content: The HTML content of the webpage
        page_url: The URL of the page being analyzed

    Returns:
        Dictionary containing extracted business information
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text content
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    extracted_info = {
        "url": page_url,
        "abn": None,
        "emails": [],
        "phones": [],
        "addresses": [],
        "business_description": None
    }

    # Extract ABN (Australian Business Number)
    abn_patterns = [
        r'\bABN:?\s*(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})\b',
        r'\bABN:?\s*(\d{11})\b',
        r'\b(\d{2}\s\d{3}\s\d{3}\s\d{3})\b'
    ]

    for pattern in abn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_info["abn"] = match.group(1).replace(' ', '')
            break

    # Extract email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    extracted_info["emails"] = list(set(emails))

    # Extract phone numbers (Australian format)
    phone_patterns = [
        r'\b(?:\+61|0)[2-478](?:[ -]?\d){8}\b',
        r'\b\d{4}\s?\d{3}\s?\d{3}\b',
        r'\b\(\d{2}\)\s?\d{4}\s?\d{4}\b'
    ]

    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    extracted_info["phones"] = list(set(phones))

    # Extract addresses
    address_patterns = [
        r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Court|Ct|Lane|Ln|Way|Place|Pl),?\s+[A-Za-z\s]+,?\s+(?:NSW|VIC|QLD|SA|WA|TAS|NT|ACT)\s+\d{4}',
    ]

    addresses = []
    for pattern in address_patterns:
        addresses.extend(re.findall(pattern, text))
    extracted_info["addresses"] = list(set(addresses))

    # Try to find business description from meta tags
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        extracted_info["business_description"] = meta_desc.get('content')

    # If no meta description, try to find from about section
    if not extracted_info["business_description"]:
        about_sections = soup.find_all(['div', 'section', 'p'],
                                      class_=re.compile('about|description|intro', re.IGNORECASE))
        if about_sections:
            desc_text = ' '.join([section.get_text().strip() for section in about_sections[:2]])
            if len(desc_text) > 50:
                extracted_info["business_description"] = desc_text[:500]

    return extracted_info


@tool
def summarize_business_data(extracted_data_list: List[Dict]) -> Dict:
    """
    Consolidate and summarize business information from multiple pages.

    Args:
        extracted_data_list: List of dictionaries containing extracted business info from different pages

    Returns:
        Consolidated business information
    """
    consolidated = {
        "abn": None,
        "emails": set(),
        "phones": set(),
        "addresses": set(),
        "business_description": None,
        "pages_visited": []
    }

    for data in extracted_data_list:
        if data.get("abn") and not consolidated["abn"]:
            consolidated["abn"] = data["abn"]

        consolidated["emails"].update(data.get("emails", []))
        consolidated["phones"].update(data.get("phones", []))
        consolidated["addresses"].update(data.get("addresses", []))

        if data.get("business_description"):
            if not consolidated["business_description"] or \
               len(data["business_description"]) > len(consolidated["business_description"]):
                consolidated["business_description"] = data["business_description"]

        consolidated["pages_visited"].append(data.get("url", "unknown"))

    # Convert sets to lists for JSON serialization
    consolidated["emails"] = list(consolidated["emails"])
    consolidated["phones"] = list(consolidated["phones"])
    consolidated["addresses"] = list(consolidated["addresses"])

    return consolidated


# Initialize the browser tool and agent at module level
# These will be reused across invocations for better performance
browser_tool = AgentCoreBrowser(region="us-west-2")

agent = Agent(
    tools=[
        browser_tool.browser,
        extract_business_info,
        summarize_business_data
    ],
    model="anthropic.claude-3-5-sonnet-20241022-v2:0"
)


@app.entrypoint
def scrape_business_handler(payload: Dict) -> Dict:
    """
    AgentCore Runtime entrypoint for business scraping.

    Expected payload format:
    {
        "website": "https://example.com.au",
        "prompt": "optional custom prompt"
    }

    Returns:
    {
        "status": "success" | "error",
        "data": {...extracted business info...},
        "error": "error message if failed"
    }
    """
    try:
        # Extract website from payload
        website_url = payload.get("website")
        custom_prompt = payload.get("prompt")

        if not website_url:
            return {
                "status": "error",
                "error": "No website URL provided in payload. Expected: {'website': 'https://example.com'}"
            }

        # Ensure URL has protocol
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        # Build prompt
        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = f"""
            Please help me gather comprehensive information about a business from their website: {website_url}

            Your task:
            1. Navigate to the website homepage
            2. Browse through important pages (like About, Contact, Home pages) to gather information
            3. Extract the following information:
               - ABN (Australian Business Number) - look for patterns like "ABN: XX XXX XXX XXX" or 11-digit numbers
               - Email addresses
               - Phone numbers (especially Australian format)
               - Physical address/location
               - Business description (what the business does, their services, etc.)

            4. Use the extract_business_info tool to analyze each page's HTML content
            5. Visit at least 2-3 different pages if possible (homepage, about page, contact page)
            6. Finally, use summarize_business_data to consolidate all findings

            Please be thorough and extract as much relevant information as possible.
            Return the final consolidated summary.
            """

        # Invoke the agent
        result = agent(prompt)

        return {
            "status": "success",
            "website": website_url,
            "data": result
        }

    except Exception as e:
        return {
            "status": "error",
            "website": payload.get("website", "unknown"),
            "error": str(e)
        }


@app.entrypoint
async def scrape_business_streaming(payload: Dict):
    """
    AgentCore Runtime entrypoint with streaming support.

    Use this for real-time updates as the agent works.

    Expected payload format:
    {
        "website": "https://example.com.au"
    }

    Yields:
    Stream of events as the agent processes the request
    """
    try:
        website_url = payload.get("website")

        if not website_url:
            yield {
                "status": "error",
                "error": "No website URL provided in payload"
            }
            return

        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url

        prompt = f"""
        Please help me gather comprehensive information about a business from their website: {website_url}

        Your task:
        1. Navigate to the website homepage
        2. Browse through important pages (like About, Contact, Home pages) to gather information
        3. Extract the following information:
           - ABN (Australian Business Number)
           - Email addresses
           - Phone numbers (especially Australian format)
           - Physical address/location
           - Business description

        4. Use the extract_business_info tool to analyze each page's HTML content
        5. Visit at least 2-3 different pages if possible
        6. Finally, use summarize_business_data to consolidate all findings

        Please be thorough and extract as much relevant information as possible.
        """

        # Stream agent responses
        stream = agent.stream_async(prompt)

        async for event in stream:
            yield {
                "status": "streaming",
                "website": website_url,
                "event": event
            }

    except Exception as e:
        yield {
            "status": "error",
            "website": payload.get("website", "unknown"),
            "error": str(e)
        }


# For local testing
if __name__ == "__main__":
    # Local testing mode
    print("Business Web Scraper - AgentCore Runtime Mode")
    print("=" * 60)
    print()

    # Test payload
    test_payload = {
        "website": "https://www.example.com.au"
    }

    print(f"Testing with payload: {json.dumps(test_payload, indent=2)}")
    print()
    print("Invoking agent...")
    print()

    result = scrape_business_handler(test_payload)
    print("Result:")
    print(json.dumps(result, indent=2))
