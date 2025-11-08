# WebPage API - WebPoet-style Parsing for RusticSoup

RusticSoup includes a powerful WebPage API inspired by web-poet, providing a high-level, declarative interface for web scraping.

## Table of Contents

- Quick Start
- Core Concepts
- API Reference
- Real-World Examples
- Comparison with web-poet

## Quick Start

```python
from rusticsoup import WebPage

# Create a WebPage from HTML
html = """
<div class="product">
    <h2>Amazing Widget</h2>
    <span class="price">$29.99</span>
    <a href="/buy">Buy Now</a>
    <img src="/widget.jpg">
</div>
"""

page = WebPage(html, url="https://example.com/products")

# Extract single values
title = page.text("h2")  # "Amazing Widget"
price = page.text("span.price")  # "$29.99"
link = page.attr("a", "href")  # "/buy"
image = page.attr("img", "src")  # "/widget.jpg"

# Extract structured data
data = page.extract({
    "title": "h2",
    "price": "span.price",
    "link": "a@href",  # @ syntax for attributes
    "image": "img@src"
})
# Returns: {'title': 'Amazing Widget', 'price': '$29.99', 'link': '/buy', 'image': '/widget.jpg'}
```

## Core Concepts

### 1. WebPage Class

The `WebPage` class represents a parsed HTML document with metadata:

```python
page = WebPage(
    html="<html>...</html>",
    url="https://example.com/page",
    metadata={"source": "api", "timestamp": "2025-01-01"}
)
```

Properties:
- `url` - The page URL
- `metadata` - Dictionary of custom metadata

Methods:
- `text(selector)` - Extract text from first matching element
- `text_all(selector)` - Extract text from all matching elements
- `attr(selector, attribute)` - Extract attribute from first matching element
- `attr_all(selector, attribute)` - Extract attribute from all matching elements
- `css(selector)` - Get HTML of first matching element
- `css_all(selector)` - Get HTML of all matching elements
- `has(selector)` - Check if selector matches any elements
- `count(selector)` - Count matching elements
- `extract(mappings)` - Extract structured data using field mappings
- `extract_all(container, mappings)` - Extract multiple items
- `absolute_url(url)` - Convert relative URL to absolute
- `html()` - Get raw HTML content

### 2. Extraction Patterns

#### Single Field Extraction

```python
# Text content
title = page.text("h1")

# Attribute extraction
link = page.attr("a", "href")

# Check existence
has_nav = page.has("nav.main-menu")

# Count elements
num_products = page.count("div.product")
```

#### Multiple Field Extraction

```python
# Extract all matching elements
all_links = page.attr_all("a", "href")
all_paragraphs = page.text_all("p")
```

#### Structured Data Extraction

```python
# Extract single item
product = page.extract({
    "title": "h2.product-title",
    "price": "span.price",
    "url": "a@href",          # @ syntax for attributes
    "image": "img@src",
    "rating": "div.rating"
})

# Extract multiple items
products = page.extract_all("div.product", {
    "title": "h2",
    "price": "span.price",
    "url": "a@href"
})
```

### 3. Field Specification Syntax

Field selectors support a special syntax for common operations:

| Syntax | Description | Example |
|--------|-------------|---------|
| `"selector"` | Extract text content | `"h1"` → "Page Title" |
| `"selector@attr"` | Extract attribute | `"a@href"` → "/page.html" |
| `"selector@get_all"` | Extract text from all matches | `"p@get_all"` → ["Para 1", "Para 2"] |
| `"selector@attr@get_all"` | Extract attribute from all matches | `"img@src@get_all"` → ["/img1.jpg", "/img2.jpg"] |

## API Reference

### WebPage

```python
class WebPage:
    def __init__(
        self,
        html: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    )
```

Properties
- `url: Optional[str]`
- `metadata: Dict[str, str]`

Methods
- `text(selector: str) -> str`
- `text_all(selector: str) -> List[str]`
- `attr(selector: str, attribute: str) -> Optional[str]`
- `attr_all(selector: str, attribute: str) -> List[str]`
- `css(selector: str) -> Optional[str]`
- `css_all(selector: str) -> List[str]`
- `has(selector: str) -> bool`
- `count(selector: str) -> int`
- `extract(field_mappings: Dict[str, str]) -> Dict[str, Any]`
- `extract_all(container_selector: str, field_mappings: Dict[str, str]) -> List[Dict[str, Any]]`
- `absolute_url(url: str) -> str`
- `html() -> str`

### Field (overview)

```python
from rusticsoup import Field

# Create field descriptors
title_field = Field(css="h1")
link_field = Field(css="a", attr="href")
tags_field = Field(css="span.tag", get_all=True)
```

Parameters:
- `css` (str, optional) - CSS selector
- `xpath` (str, optional) - XPath selector (planned)
- `attr` (str, optional) - Attribute name to extract
- `get_all` (bool, default=False) - Extract from all matching elements
- `default` (str, optional) - Default value if not found
- `required` (bool, default=True) - Whether the field is required

## Real-World Examples

### Example 1: E-commerce Product Scraping

```python
from rusticsoup import WebPage

html = """
<div class="product" data-id="123">
    <h2 class="title">Wireless Mouse</h2>
    <div class="price">
        <span class="current">$24.99</span>
        <span class="original">$34.99</span>
    </div>
    <div class="rating">
        <span class="stars">★★★★☆</span>
        <span class="count">1,234 reviews</span>
    </div>
    <a href="/products/wireless-mouse" class="view-details">View Details</a>
    <img src="/images/mouse.jpg" alt="Wireless Mouse">
    <ul class="features">
        <li>Ergonomic design</li>
        <li>Wireless connectivity</li>
        <li>Long battery life</li>
    </ul>
</div>
"""

page = WebPage(html, url="https://shop.example.com")

# Extract product data
product = page.extract({
    "title": "h2.title",
    "current_price": "span.current",
    "original_price": "span.original",
    "rating": "span.stars",
    "review_count": "span.count",
    "url": "a.view-details@href",
    "image": "img@src",
    "image_alt": "img@alt"
})

# Convert to absolute URL
product["url"] = page.absolute_url(product["url"])
product["image"] = page.absolute_url(product["image"])

print(product)
```

### Example 2: News Article Scraping

```python
from rusticsoup import WebPage

html = """
<article class="news-article">
    <header>
        <h1>Breaking: New Technology Breakthrough</h1>
        <div class="meta">
            <span class="author">By John Doe</span>
            <time datetime="2025-01-07">January 7, 2025</time>
            <span class="category">Technology</span>
        </div>
    </header>
    <div class="content">
        <p class="lead">Scientists have announced a major breakthrough...</p>
        <p>The research team, led by Dr. Smith...</p>
        <p>This discovery could lead to...</p>
    </div>
    <div class="tags">
        <a href="/tag/science">Science</a>
        <a href="/tag/technology">Technology</a>
        <a href="/tag/research">Research</a>
    </div>
</article>
"""

page = WebPage(html, url="https://news.example.com/article/123")

# Extract article data
article = page.extract({
    "title": "h1",
    "author": "span.author",
    "date": "time@datetime",
    "category": "span.category",
    "lead": "p.lead"
})

# Extract all paragraphs
article["paragraphs"] = page.text_all("div.content p")

# Extract all tags
article["tags"] = page.text_all("div.tags a")
article["tag_urls"] = page.attr_all("div.tags a", "href")

print(article)
```

### Example 3: Search Results Scraping

```python
from rusticsoup import WebPage

html = """
<div class="search-results">
    <div class="result">
        <h3><a href="/item/1">First Result</a></h3>
        <p class="description">Description of first result...</p>
        <span class="price">$10.00</span>
    </div>
    <div class="result">
        <h3><a href="/item/2">Second Result</a></h3>
        <p class="description">Description of second result...</p>
        <span class="price">$20.00</span>
    </div>
    <div class="result">
        <h3><a href="/item/3">Third Result</a></h3>
        <p class="description">Description of third result...</p>
        <span class="price">$30.00</span>
    </div>
</div>
"""

page = WebPage(html, url="https://example.com/search")

# Extract all results at once
results = page.extract_all("div.result", {
    "title": "h3 a",
    "url": "h3 a@href",
    "description": "p.description",
    "price": "span.price"
})

# Post-process results
for result in results:
    result["url"] = page.absolute_url(result["url"])
    # Clean price
    result["price_value"] = float(result["price"].replace("$", ""))

print(f"Found {len(results)} results")
```

## Comparison with web-poet

RusticSoup's WebPage API is inspired by web-poet but optimized for speed and simplicity.

| Feature | web-poet | RusticSoup WebPage | Notes |
|---------|----------|-------------------|-------|
| Language | Python | Rust + Python | RusticSoup is 2-10x faster |
| WebPage class | ✅ | ✅ | Similar API design |
| CSS selectors | ✅ | ✅ | Full support |
| XPath | ✅ | Planned | Coming soon |
| Field descriptors | ✅ | ✅ | For PageObject pattern |
| PageObject pattern | ✅ | Partial | Field class available |
| Dependency injection | ✅ | Planned | Future feature |
| URL resolution | ✅ | ✅ | `absolute_url()` method |
| Metadata | ✅ | ✅ | Custom metadata support |
| Browser support | Via scrapy-poet | ❌ | Not planned |
| Async support | ✅ | ❌ | Not needed (Rust speed) |

## Best Practices

1. Use specific selectors
2. Handle missing data
3. Process URLs with `absolute_url`
4. Prefer batch extraction with `extract`/`extract_all`

## Future Enhancements

- XPath Support
- Complete PageObject implementation
- Nested extraction
- Plugins for custom processors
- Type validation and conversion
- Selector caching

## See Also

- RusticSoup Main README: ../../README.md
- Quick Start: ./quickstart.md
- Field Usage Guide: ./field_usage.md
- Containers & Mappings Guide: ./containers_and_mappings.md
- PageObject Pattern: ./page_object_pattern.md
- Test Examples: ../../test_webpage_api.py
