"""
JSON extraction utilities for RusticSoup.

Extract JSON from script tags, JSON-LD structured data, and other embedded JSON.
"""

import json
import re
from typing import Any, Optional


def extract_json_ld(html: str) -> list[dict[str, Any]]:
    """
    Extract JSON-LD structured data from HTML.

    Args:
        html: HTML content

    Returns:
        List of JSON-LD objects found

    Examples:
        >>> html = '<script type="application/ld+json">{"@type": "Product"}</script>'
        >>> extract_json_ld(html)
        [{'@type': 'Product'}]
    """
    results = []
    pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

    for match in matches:
        try:
            data = json.loads(match.strip())
            results.append(data)
        except json.JSONDecodeError:
            continue

    return results


def extract_json_from_script(
    html: str, pattern: Optional[str] = None
) -> list[dict[str, Any]]:
    """
    Extract JSON objects from script tags.

    Args:
        html: HTML content
        pattern: Optional regex pattern to find specific JSON (e.g., r'window\\.data = (\\{.*?\\});')

    Returns:
        List of JSON objects found

    Examples:
        >>> html = '<script>var data = {"key": "value"};</script>'
        >>> extract_json_from_script(html)
        [{'key': 'value'}]
    """
    results = []

    if pattern:
        # Use custom pattern
        matches = re.findall(pattern, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match)
                results.append(data)
            except json.JSONDecodeError:
                continue
    else:
        # Find all script tags
        script_pattern = r"<script[^>]*>(.*?)</script>"
        scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)

        for script in scripts:
            # Try to find JSON objects in the script
            # Look for {...} patterns
            json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
            potential_jsons = re.findall(json_pattern, script)

            for potential in potential_jsons:
                try:
                    data = json.loads(potential)
                    if isinstance(data, dict) and data:  # Only add non-empty dicts
                        results.append(data)
                except json.JSONDecodeError:
                    continue

    return results


def extract_json_variable(html: str, variable_name: str) -> Optional[dict[str, Any]]:
    """
    Extract JSON assigned to a specific JavaScript variable.

    Args:
        html: HTML content
        variable_name: Name of the JavaScript variable

    Returns:
        JSON object or None

    Examples:
        >>> html = '<script>window.pageData = {"id": 123};</script>'
        >>> extract_json_variable(html, "pageData")
        {'id': 123}
    """
    # Pattern to match variable assignment
    pattern = rf"{re.escape(variable_name)}\s*=\s*(\{{.*?\}});"
    match = re.search(pattern, html, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    return None


def find_json_in_text(text: str) -> list[dict[str, Any]]:
    """
    Find all JSON objects in text.

    Args:
        text: Text that may contain JSON

    Returns:
        List of JSON objects found
    """
    results = []

    # Find potential JSON objects
    pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    matches = re.findall(pattern, text)

    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, dict) and data:
                results.append(data)
        except json.JSONDecodeError:
            continue

    return results


def extract_json_by_key(html: str, key: str) -> list[Any]:
    """
    Extract all JSON objects that contain a specific key.

    Args:
        html: HTML content
        key: JSON key to search for

    Returns:
        List of values for the specified key

    Examples:
        >>> html = '<script>{"products": [{"id": 1}, {"id": 2}]}</script>'
        >>> extract_json_by_key(html, "products")
        [[{'id': 1}, {'id': 2}]]
    """
    results = []
    all_json = extract_json_from_script(html)

    def find_key(obj: Any, target_key: str):
        """Recursively find key in nested structure"""
        if isinstance(obj, dict):
            if target_key in obj:
                results.append(obj[target_key])
            for value in obj.values():
                find_key(value, target_key)
        elif isinstance(obj, list):
            for item in obj:
                find_key(item, target_key)

    for json_obj in all_json:
        find_key(json_obj, key)

    return results


__all__ = [
    "extract_json_ld",
    "extract_json_from_script",
    "extract_json_variable",
    "find_json_in_text",
    "extract_json_by_key",
]
