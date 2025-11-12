#!/usr/bin/env python3
"""
Simple example demonstrating the Business Scraper Agent.

This script shows how to use the agent programmatically by importing
the handler function from runtime_agent.py
"""

import os
import json
from dotenv import load_dotenv

# Import the handler from runtime_agent
from runtime_agent import scrape_business_handler

# Load environment variables
load_dotenv()


def example_single_website():
    """Example: Scrape a single website."""
    print("Example 1: Single Website Scraping")
    print("-" * 60)

    # Scrape website by calling the handler directly
    website = "https://www.example.com.au"
    print(f"Scraping: {website}\n")

    payload = {"website": website}
    result = scrape_business_handler(payload)
    print(json.dumps(result, indent=2))
    print("\n")


def example_multiple_websites():
    """Example: Scrape multiple websites."""
    print("Example 2: Multiple Websites Scraping")
    print("-" * 60)

    # List of websites to scrape
    websites = [
        "https://www.example1.com.au",
        "https://www.example2.com.au",
        "https://www.example3.com.au"
    ]

    # Scrape each website
    results = []
    for website in websites:
        print(f"\nScraping: {website}")
        payload = {"website": website}
        result = scrape_business_handler(payload)
        results.append(result)
        print("✓ Complete")

    # Save all results
    output_file = "multiple_businesses.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ All results saved to: {output_file}\n")


def example_with_validation():
    """Example: Scrape and validate results."""
    print("Example 3: Scraping with Validation")
    print("-" * 60)

    from tools.validation import validate_abn, validate_email, format_business_data

    # Scrape website
    website = "https://www.example.com.au"
    print(f"Scraping: {website}\n")

    payload = {"website": website}
    result = scrape_business_handler(payload)

    # Extract data from response
    data = result.get("data", {})

    # Validate ABN if found
    if data.get("abn"):
        is_valid = validate_abn(data["abn"])
        print(f"ABN: {data['abn']} - {'✓ Valid' if is_valid else '✗ Invalid'}")

    # Validate emails if found
    if data.get("emails"):
        print("\nEmails:")
        for email in data["emails"]:
            is_valid = validate_email(email)
            print(f"  {email} - {'✓ Valid' if is_valid else '✗ Invalid'}")

    # Format and display nicely
    if data:
        print("\n" + format_business_data(data))


def example_custom_prompt():
    """Example: Use custom prompt for specific information."""
    print("Example 4: Custom Prompt")
    print("-" * 60)

    # Custom prompt focusing on specific information
    website = "https://www.example.com.au"
    custom_prompt = """
    Focus specifically on finding:
    1. The company's ABN
    2. The main contact email
    3. The business address

    Be thorough but concise. Only return these three pieces of information.
    """

    print(f"Using custom prompt for: {website}\n")

    payload = {
        "website": website,
        "prompt": custom_prompt
    }

    result = scrape_business_handler(payload)
    print(json.dumps(result, indent=2))
    print("\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Business Scraper Agent - Examples")
    print("=" * 60)
    print()

    # Uncomment the example you want to run:

    # Example 1: Basic single website scraping
    example_single_website()

    # Example 2: Scrape multiple websites
    # example_multiple_websites()

    # Example 3: Scraping with validation
    # example_with_validation()

    # Example 4: Custom prompt
    # example_custom_prompt()
