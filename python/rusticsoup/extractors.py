"""
Common data extractors and converters for RusticSoup.

This module provides pre-built extractors for common data types like prices,
dates, emails, phone numbers, and URLs.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Union


def extract_price(text: str, currency: str = "USD") -> Optional[float]:
    """
    Extract price from text string.

    Args:
        text: Text containing price (e.g., "$99.99", "€50,00")
        currency: Currency code (USD, EUR, GBP, etc.)

    Returns:
        Float price or None if not found

    Examples:
        >>> extract_price("$99.99")
        99.99
        >>> extract_price("Price: $1,234.56")
        1234.56
        >>> extract_price("€50,00")
        50.0
    """
    if not text:
        return None

    # Remove currency symbols and clean
    cleaned = re.sub(r"[^\d,.\s-]", "", text)

    # Handle European format (1.234,56)
    if "," in cleaned and "." in cleaned:
        # If comma comes after period, it's European format
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            # US format
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Check if it's used as decimal (50,00) or thousands (1,000)
        parts = cleaned.split(",")
        if len(parts[-1]) == 2:  # Likely decimal
            cleaned = cleaned.replace(",", ".")
        else:  # Likely thousands
            cleaned = cleaned.replace(",", "")

    # Extract number
    match = re.search(r"-?\d+\.?\d*", cleaned)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


def extract_decimal(text: str) -> Optional[Decimal]:
    """
    Extract decimal value from text (more precise than float).

    Args:
        text: Text containing decimal number

    Returns:
        Decimal value or None
    """
    price = extract_price(text)
    return Decimal(str(price)) if price is not None else None


def extract_int(text: str) -> Optional[int]:
    """
    Extract integer from text.

    Args:
        text: Text containing integer

    Returns:
        Integer or None

    Examples:
        >>> extract_int("Quantity: 42 items")
        42
        >>> extract_int("1,234 sold")
        1234
    """
    if not text:
        return None

    # Remove commas and extract digits
    cleaned = text.replace(",", "")
    match = re.search(r"-?\d+", cleaned)
    if match:
        try:
            return int(match.group())
        except ValueError:
            return None
    return None


def extract_bool(text: str, true_values: Optional[list] = None) -> bool:
    """
    Convert text to boolean.

    Args:
        text: Text to convert
        true_values: List of strings considered True (case-insensitive)

    Returns:
        Boolean value

    Examples:
        >>> extract_bool("In Stock")
        True
        >>> extract_bool("Out of Stock")
        False
        >>> extract_bool("yes")
        True
    """
    if not text:
        return False

    if true_values is None:
        true_values = [
            "true",
            "yes",
            "y",
            "1",
            "available",
            "in stock",
            "enabled",
            "active",
            "on",
        ]

    text_lower = text.lower().strip()
    return any(val.lower() in text_lower for val in true_values)


def extract_email(text: str) -> Optional[str]:
    """
    Extract email address from text.

    Args:
        text: Text containing email

    Returns:
        Email address or None

    Examples:
        >>> extract_email("Contact: john@example.com")
        'john@example.com'
    """
    if not text:
        return None

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_emails(text: str) -> list[str]:
    """
    Extract all email addresses from text.

    Args:
        text: Text containing emails

    Returns:
        List of email addresses
    """
    if not text:
        return []

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    return re.findall(pattern, text)


def extract_phone(text: str, country: str = "US") -> Optional[str]:
    """
    Extract phone number from text.

    Args:
        text: Text containing phone number
        country: Country code for format (US, UK, etc.)

    Returns:
        Phone number or None

    Examples:
        >>> extract_phone("Call: (555) 123-4567")
        '(555) 123-4567'
    """
    if not text:
        return None

    # US format
    if country == "US":
        patterns = [
            r"\(\d{3}\)\s*\d{3}[-\s]?\d{4}",  # (555) 123-4567
            r"\d{3}[-\s]?\d{3}[-\s]?\d{4}",  # 555-123-4567
            r"\+1\s?\d{3}[-\s]?\d{3}[-\s]?\d{4}",  # +1 555-123-4567
        ]
    else:
        # International format
        patterns = [r"\+\d{1,3}[-\s]?\d{1,4}[-\s]?\d{1,4}[-\s]?\d{1,9}"]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None


def extract_url(text: str) -> Optional[str]:
    """
    Extract URL from text.

    Args:
        text: Text containing URL

    Returns:
        URL or None
    """
    if not text:
        return None

    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(pattern, text)
    return match.group() if match else None


def extract_urls(text: str) -> list[str]:
    """
    Extract all URLs from text.

    Args:
        text: Text containing URLs

    Returns:
        List of URLs
    """
    if not text:
        return []

    pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(pattern, text)


def clean_text(
    text: str,
    strip: bool = True,
    collapse_spaces: bool = True,
    remove_extra_whitespace: bool = True,
) -> str:
    """
    Clean and normalize text.

    Args:
        text: Text to clean
        strip: Strip leading/trailing whitespace
        collapse_spaces: Replace multiple spaces with single space
        remove_extra_whitespace: Remove tabs, newlines, etc.

    Returns:
        Cleaned text

    Examples:
        >>> clean_text("  Hello   World  \\n\\t")
        'Hello World'
    """
    if not text:
        return ""

    if remove_extra_whitespace:
        text = re.sub(r"\s+", " ", text)

    if collapse_spaces:
        text = " ".join(text.split())

    if strip:
        text = text.strip()

    return text


def extract_date(text: str, formats: Optional[list[str]] = None) -> Optional[datetime]:
    """
    Extract date from text using common formats.

    Args:
        text: Text containing date
        formats: List of strptime format strings to try

    Returns:
        datetime object or None

    Examples:
        >>> extract_date("Posted on Jan 7, 2025")
        datetime.datetime(2025, 1, 7, 0, 0)
    """
    if not text:
        return None

    if formats is None:
        formats = [
            "%Y-%m-%d",  # 2025-01-07
            "%m/%d/%Y",  # 01/07/2025
            "%d/%m/%Y",  # 07/01/2025
            "%B %d, %Y",  # January 7, 2025
            "%b %d, %Y",  # Jan 7, 2025
            "%Y-%m-%dT%H:%M:%S",  # ISO format
            "%Y-%m-%d %H:%M:%S",  # SQL format
        ]

    # Try each format
    for fmt in formats:
        try:
            # Extract date-like pattern from text
            date_match = re.search(r"[\w\s,:-]+", text)
            if date_match:
                return datetime.strptime(date_match.group().strip(), fmt)
        except ValueError:
            continue

    return None


# Type converters for Field types
TYPE_CONVERTERS = {
    "float": extract_price,
    "int": extract_int,
    "bool": extract_bool,
    "decimal": extract_decimal,
    "email": extract_email,
    "phone": extract_phone,
    "url": extract_url,
    "date": extract_date,
    "datetime": extract_date,
}


def convert_type(value: Any, target_type: Union[type, str]) -> Any:
    """
    Convert value to target type using appropriate extractor.

    Args:
        value: Value to convert
        target_type: Target type (type object or string name)

    Returns:
        Converted value
    """
    if value is None:
        return None

    # Handle string type names
    if isinstance(target_type, str):
        type_name = target_type.lower()
        if type_name in TYPE_CONVERTERS:
            return TYPE_CONVERTERS[type_name](str(value))
        return value

    # Handle type objects
    if target_type is float:
        return extract_price(str(value))
    elif target_type is int:
        return extract_int(str(value))
    elif target_type is bool:
        return extract_bool(str(value))
    elif target_type is Decimal:
        return extract_decimal(str(value))
    elif target_type is str:
        return clean_text(str(value))

    return value


__all__ = [
    "extract_price",
    "extract_decimal",
    "extract_int",
    "extract_bool",
    "extract_email",
    "extract_emails",
    "extract_phone",
    "extract_url",
    "extract_urls",
    "clean_text",
    "extract_date",
    "convert_type",
    "TYPE_CONVERTERS",
]
