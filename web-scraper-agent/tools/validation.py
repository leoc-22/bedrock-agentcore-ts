"""
Validation tools for business information extraction.
"""

import re
from typing import Optional
from strands import tool


@tool
def validate_abn(abn: str) -> bool:
    """
    Validate an Australian Business Number (ABN).

    ABN validation uses a weighted checksum algorithm.
    Format: 11 digits (XX XXX XXX XXX)

    Args:
        abn: The ABN to validate (with or without spaces)

    Returns:
        True if valid, False otherwise
    """
    # Remove spaces and non-digits
    abn = re.sub(r'\D', '', abn)

    # Check if 11 digits
    if len(abn) != 11:
        return False

    # ABN checksum validation
    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]

    # Subtract 1 from first digit
    digits = [int(abn[0]) - 1] + [int(d) for d in abn[1:]]

    # Calculate weighted sum
    weighted_sum = sum(digit * weight for digit, weight in zip(digits, weights))

    # Check if divisible by 89
    return weighted_sum % 89 == 0


@tool
def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: The email address to validate

    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@tool
def validate_australian_phone(phone: str) -> bool:
    """
    Validate Australian phone number format.

    Accepts formats:
    - +61 X XXXX XXXX
    - 0X XXXX XXXX
    - (0X) XXXX XXXX

    Args:
        phone: The phone number to validate

    Returns:
        True if valid Australian format, False otherwise
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)

    # Check for valid Australian phone patterns
    if digits.startswith('61'):
        # International format: should be 11 digits (61 + 9 digits)
        return len(digits) == 11
    elif digits.startswith('0'):
        # Local format: should be 10 digits
        return len(digits) == 10
    else:
        return False


@tool
def format_business_data(data: dict) -> str:
    """
    Format extracted business data into a readable string.

    Args:
        data: Dictionary containing business information

    Returns:
        Formatted string representation of the data
    """
    lines = []
    lines.append("=" * 60)
    lines.append("BUSINESS INFORMATION")
    lines.append("=" * 60)

    if data.get("abn"):
        abn_valid = validate_abn(data["abn"])
        status = "✓ Valid" if abn_valid else "✗ Invalid format"
        lines.append(f"\nABN: {data['abn']} ({status})")

    if data.get("emails"):
        lines.append(f"\nEmail Addresses:")
        for email in data["emails"]:
            valid = validate_email(email)
            status = "✓" if valid else "✗"
            lines.append(f"  {status} {email}")

    if data.get("phones"):
        lines.append(f"\nPhone Numbers:")
        for phone in data["phones"]:
            valid = validate_australian_phone(phone)
            status = "✓" if valid else "✗"
            lines.append(f"  {status} {phone}")

    if data.get("addresses"):
        lines.append(f"\nAddresses:")
        for address in data["addresses"]:
            lines.append(f"  • {address}")

    if data.get("business_description"):
        lines.append(f"\nBusiness Description:")
        lines.append(f"  {data['business_description']}")

    if data.get("pages_visited"):
        lines.append(f"\nPages Visited: {len(data['pages_visited'])}")
        for url in data["pages_visited"]:
            lines.append(f"  • {url}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
