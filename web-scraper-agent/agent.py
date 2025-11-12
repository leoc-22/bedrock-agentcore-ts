#!/usr/bin/env python3
"""
Business Web Scraper Agent using Strands Agents and Bedrock AgentCore Browser Tool

This agent uses the built-in Browser Tool from Bedrock AgentCore to:
1. Navigate business websites
2. Browse multiple pages to gather information
3. Extract ABN, contact information, location details, and business descriptions
"""

import os
import json
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv
from strands import Agent, tool
from strands_tools.browser import AgentCoreBrowser

# Load environment variables
load_dotenv()


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
    # Format: XX XXX XXX XXX or XXXXXXXXXXX
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

    # Extract addresses (look for common Australian address patterns)
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
        # Keep first found ABN
        if data.get("abn") and not consolidated["abn"]:
            consolidated["abn"] = data["abn"]

        # Collect all emails
        consolidated["emails"].update(data.get("emails", []))

        # Collect all phones
        consolidated["phones"].update(data.get("phones", []))

        # Collect all addresses
        consolidated["addresses"].update(data.get("addresses", []))

        # Keep longest business description
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


class BusinessScraperAgent:
    """Main agent class for scraping business information from websites."""

    def __init__(self, region: str = "us-west-2"):
        """
        Initialize the Business Scraper Agent.

        Args:
            region: AWS region for Bedrock AgentCore Browser
        """
        self.region = region

        # Initialize AgentCore Browser
        self.browser_tool = AgentCoreBrowser(region=self.region)

        # Create the agent with browser and custom extraction tools
        self.agent = Agent(
            tools=[
                self.browser_tool.browser,
                extract_business_info,
                summarize_business_data
            ],
            model="anthropic.claude-3-5-sonnet-20241022-v2:0"  # Use Claude Sonnet for better reasoning
        )

    def scrape_business(self, website_url: str) -> Dict:
        """
        Scrape business information from a website.

        Args:
            website_url: The business website URL to scrape

        Returns:
            Dictionary containing extracted business information
        """
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

        try:
            response = self.agent(prompt)
            return response
        except Exception as e:
            return {
                "error": str(e),
                "website": website_url
            }


def main():
    """Main entry point for the business scraper agent."""

    # Get configuration from environment
    aws_region = os.getenv("AWS_REGION", "us-west-2")

    print("=" * 80)
    print("Business Web Scraper Agent")
    print("Powered by AWS Bedrock AgentCore + Strands Agents")
    print("=" * 80)
    print()

    # Initialize the agent
    print(f"Initializing agent in region: {aws_region}")
    scraper = BusinessScraperAgent(region=aws_region)
    print("Agent initialized successfully!")
    print()

    # Get website URL from user or environment
    website = os.getenv("TARGET_WEBSITE")

    if not website:
        website = input("Enter business website URL: ").strip()

    if not website:
        print("Error: No website URL provided")
        return

    # Ensure URL has protocol
    if not website.startswith(('http://', 'https://')):
        website = 'https://' + website

    print(f"\nScraping business information from: {website}")
    print("This may take a moment as the agent browses the website...")
    print()

    # Scrape the website
    result = scraper.scrape_business(website)

    # Display results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print()
    print(json.dumps(result, indent=2))
    print()

    # Save results to file
    output_file = "business_info.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
