# Field Transform Documentation

## Overview

The `transform` parameter allows you to apply one or more callable functions to transform extracted values. This enables powerful data processing pipelines directly within your field definitions.

## Basic Usage

### Single Transform

Apply a single transformation function:

```python
from rusticsoup import WebPage, Field

html = "<h1>hello world</h1>"
page = WebPage(html)

# Single transform
field = Field(css="h1", transform=str.upper)
result = field.extract(page)  # "HELLO WORLD"
```

### Multiple Transforms (Pipeline)

Chain multiple transforms that are applied in order:

```python
field = Field(
    css="h1",
    transform=[
        str.strip,      # First: strip whitespace
        str.upper,      # Second: convert to uppercase
        lambda s: s.replace(" ", "_")  # Third: replace spaces with underscores
    ]
)
result = field.extract(page)  # "HELLO_WORLD"
```

## Using with ItemPage

Transforms integrate seamlessly with the PageObject pattern:

```python
from rusticsoup_helpers import ItemPage

class Article(ItemPage):
    title = Field(css="h1", transform=str.upper)
    author = Field(css=".author", transform=str.title)
    price = Field(
        css=".price",
        transform=[
            str.strip,
            lambda s: float(s.replace("$", ""))
        ]
    )

page = WebPage(html)
article = Article(page)

print(article.title)   # "UNDERSTANDING RUST"
print(article.author)  # "John Doe"
print(article.price)   # 19.99
```

## Transform with get_all

Transforms can process entire lists:

```python
html = """
<span class="tag">python</span>
<span class="tag">rust</span>
<span class="tag">javascript</span>
"""

def uppercase_list(items):
    return [item.upper() for item in items]

field = Field(css=".tag", get_all=True, transform=uppercase_list)
result = field.extract(page)  # ["PYTHON", "RUST", "JAVASCRIPT"]
```

## Transform with attr

Transforms work with attribute extraction:

```python
field = Field(
    css="a",
    attr="href",
    transform=lambda href: f"https://example.com{href}"
)
result = field.extract(page)  # "https://example.com/product/123"
```

## Real-World Examples

### Article Extraction

```python
def clean_author(text):
    """Remove 'by' prefix and title case"""
    return text.replace("by ", "").title()

def format_date(date_str):
    """Format ISO date to readable format"""
    from datetime import datetime
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%B %d, %Y")

def join_paragraphs(paragraphs):
    """Join list of paragraphs with double newline"""
    return "\n\n".join(paragraphs)

class Article(ItemPage):
    title = Field(
        css="h1",
        transform=[str.strip, str.title]
    )
    author = Field(
        css=".author",
        transform=clean_author
    )
    date = Field(
        css="time",
        attr="datetime",
        transform=format_date
    )
    content = Field(
        css=".content p",
        get_all=True,
        transform=join_paragraphs
    )
    tags = Field(
        css=".tag",
        get_all=True,
        transform=lambda tags: [t.upper() for t in tags]
    )
```

### Price Extraction

```python
import re

def extract_price(text):
    """Extract price from text like 'Price: $1,234.56'"""
    match = re.search(r'\$([0-9,]+\.[0-9]{2})', text)
    return match.group(1) if match else "0.00"

def remove_commas(price_str):
    """Remove thousand separators"""
    return price_str.replace(",", "")

def to_float(price_str):
    """Convert string to float"""
    return float(price_str)

class Product(ItemPage):
    price = Field(
        css=".price-container",
        transform=[extract_price, remove_commas, to_float]
    )
```

### URL Normalization

```python
class ProductPage(ItemPage):
    # Make relative URLs absolute
    image_urls = Field(
        css="img.product",
        attr="src",
        get_all=True,
        transform=lambda urls: [
            url if url.startswith('http') else f'https://example.com{url}'
            for url in urls
        ]
    )

    # Clean and normalize product IDs
    product_id = Field(
        css=".product-id",
        transform=[
            str.strip,
            str.upper,
            lambda s: s.replace("-", "")
        ]
    )
```

### Text Cleaning

```python
def clean_text(text):
    """Remove extra whitespace and normalize"""
    import re
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_html_entities(text):
    """Convert HTML entities to characters"""
    import html
    return html.unescape(text)

class BlogPost(ItemPage):
    content = Field(
        css=".post-content",
        transform=[
            remove_html_entities,
            clean_text
        ]
    )
```

## Transform Execution Order

Transforms are executed in the order they appear in the list:

```python
Field(
    css="h1",
    transform=[
        func1,  # Applied first
        func2,  # Applied second
        func3   # Applied third
    ]
)
```

Each function receives the output of the previous function:
```
extracted_value -> func1 -> func2 -> func3 -> final_value
```

## Error Handling

If a transform raises an exception, the extraction will fail:

```python
def strict_float(value):
    """Convert to float, raise error if invalid"""
    return float(value)

field = Field(css=".price", transform=strict_float)

try:
    result = field.extract(page)
except ValueError as e:
    print(f"Invalid price format: {e}")
```

## Best Practices

### 1. Keep Transforms Simple

Each transform should do one thing:

```python
# Good: Small, focused transforms
transform=[str.strip, str.upper, remove_prefix]

# Less ideal: One large transform doing everything
transform=lambda s: remove_prefix(s.strip().upper())
```

### 2. Make Transforms Reusable

Define transforms as functions for reuse:

```python
def clean_text(text):
    return text.strip().replace("\n", " ")

def to_float(value):
    return float(value.replace(",", ""))

# Reuse across fields
class Product(ItemPage):
    title = Field(css="h1", transform=clean_text)
    description = Field(css=".desc", transform=clean_text)
    price = Field(css=".price", transform=to_float)
```

### 3. Handle None/Empty Values

Be defensive in your transforms:

```python
def safe_upper(text):
    """Uppercase, handling None/empty"""
    return text.upper() if text else ""

def safe_float(value):
    """Convert to float, default to 0.0"""
    try:
        return float(value.replace(",", ""))
    except (ValueError, AttributeError):
        return 0.0
```

### 4. Document Complex Transforms

Add docstrings to explain what transforms do:

```python
def normalize_phone(phone):
    """
    Normalize phone number to format: (XXX) XXX-XXXX

    Handles formats:
    - XXX-XXX-XXXX
    - (XXX) XXX-XXXX
    - XXX.XXX.XXXX
    """
    digits = ''.join(c for c in phone if c.isdigit())
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
```

## Type Hints

Use type hints for better IDE support:

```python
from typing import List, Callable

def uppercase_list(items: List[str]) -> List[str]:
    return [item.upper() for item in items]

def to_float(value: str) -> float:
    return float(value.replace(",", ""))
```

## Comparison with Other Approaches

### Before Transforms (Manual Processing)

```python
class Article(ItemPage):
    title = Field(css="h1")

page = WebPage(html)
article = Article(page)

# Manual post-processing
title = article.title.strip().upper()
```

### With Transforms (Automatic Processing)

```python
class Article(ItemPage):
    title = Field(css="h1", transform=[str.strip, str.upper])

page = WebPage(html)
article = Article(page)

# Already processed!
title = article.title  # Clean and uppercase
```

## Performance Considerations

- Transforms run on every extraction
- For expensive operations, consider caching:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_transform(value):
    # Expensive operation
    return processed_value
```

## Limitations

1. Transforms must be callable (functions, lambdas, or objects with `__call__`)
2. Transform lists can have any number of items
3. Each transform must accept one argument (the value)
4. Transforms cannot access the WebPage object directly (use custom functions if needed)

## See Also

- Field Usage Guide: ./field_usage.md
- PageObject Pattern: ./page_object_pattern.md
- WebPage API: ./webpage_api.md
