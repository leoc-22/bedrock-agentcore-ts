#!/usr/bin/env python3
"""
Simple example demonstrating the Business Scraper Agent.

This script shows how to use the agent programmatically.
"""

import os
import json
from dotenv import load_dotenv
from agent import BusinessScraperAgent

# Load environment variables
load_dotenv()


def example_single_website():
    """Example: Scrape a single website."""
    print("Example 1: Single Website Scraping")
    print("-" * 60)

    # Initialize agent
    region = os.getenv("AWS_REGION", "us-west-2")
    scraper = BusinessScraperAgent(region=region)

    # Scrape website
    website = "https://www.example.com.au"
    print(f"Scraping: {website}\n")

    result = scraper.scrape_business(website)
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

    # Initialize agent once
    region = os.getenv("AWS_REGION", "us-west-2")
    scraper = BusinessScraperAgent(region=region)

    # Scrape each website
    results = []
    for website in websites:
        print(f"\nScraping: {website}")
        result = scraper.scrape_business(website)
        results.append({
            "website": website,
            "data": result
        })
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

    # Initialize and scrape
    region = os.getenv("AWS_REGION", "us-west-2")
    scraper = BusinessScraperAgent(region=region)

    website = "https://www.example.com.au"
    print(f"Scraping: {website}\n")

    result = scraper.scrape_business(website)

    # Validate ABN if found
    if result.get("abn"):
        is_valid = validate_abn(result["abn"])
        print(f"ABN: {result['abn']} - {'✓ Valid' if is_valid else '✗ Invalid'}")

    # Validate emails if found
    if result.get("emails"):
        print("\nEmails:")
        for email in result["emails"]:
            is_valid = validate_email(email)
            print(f"  {email} - {'✓ Valid' if is_valid else '✗ Invalid'}")

    # Format and display nicely
    print("\n" + format_business_data(result))


def example_custom_prompt():
    """Example: Use custom prompt for specific information."""
    print("Example 4: Custom Prompt")
    print("-" * 60)

    region = os.getenv("AWS_REGION", "us-west-2")
    scraper = BusinessScraperAgent(region=region)

    # Custom prompt focusing on specific information
    website = "https://www.example.com.au"
    custom_prompt = f"""
    Please visit {website} and focus specifically on finding:
    1. The company's ABN
    2. The main contact email
    3. The business address

    Be thorough but concise. Only return these three pieces of information.
    """

    print(f"Using custom prompt for: {website}\n")
    result = scraper.agent(custom_prompt)
    print(result)
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
