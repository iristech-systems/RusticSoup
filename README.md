# RusticSoup 🦀🍲

> Lightning-fast HTML parser and data extractor built in Rust

[![PyPI version](https://badge.fury.io/py/rusticsoup.svg)](https://badge.fury.io/py/rusticsoup)
[![Python versions](https://img.shields.io/pypi/pyversions/rusticsoup.svg)](https://pypi.org/project/rusticsoup/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Why RusticSoup?

| Feature | BeautifulSoup | RusticSoup | Speedup |
|---------|---------------|------------|---------|
| **Google Shopping** | 8.1ms | 3.9ms | **2.1x faster** |
| **Product grids** | 14ms | 1.2ms | **12x faster** |
| **Bulk processing** | Sequential | Parallel | **Up to 100x faster** |
| **Attribute extraction** | Manual loops | `@href` syntax | **Zero loops needed** |
| **WebPage API** | ❌ | ✅ | **web-poet inspired** |
| **CSS selectors** | ✅ | ✅ | Same API |
| **Memory usage** | High | Low | Rust efficiency |

## ⚡ Quick Start

```bash
pip install rusticsoup
```

### Option 1: WebPage API (Recommended - web-poet style)

```python
from rusticsoup import WebPage

html = """
<div class="product">
    <h2>Amazing Product</h2>
    <span class="price">$29.99</span>
    <a href="/buy" class="buy-btn">Buy Now</a>
    <img src="/image.jpg" alt="product">
</div>
"""

# Create a WebPage
page = WebPage(html, url="https://example.com/products")

# Extract single values
title = page.text("h2")                    # "Amazing Product"
price = page.text("span.price")            # "$29.99"
link = page.attr("a.buy-btn", "href")      # "/buy"

# Or extract structured data
product = page.extract({
    "title": "h2",
    "price": "span.price",
    "link": "a.buy-btn@href",   # @ syntax for attributes
    "image": "img@src"
})
# {'title': 'Amazing Product', 'price': '$29.99', 'link': '/buy', 'image': '/image.jpg'}
```

### Option 2: Universal Extraction (Original API)

```python
import rusticsoup

# Define what you want to extract
field_mappings = {
    "title": "h2",              # Text content
    "price": "span.price",      # Text content
    "link": "a.buy-btn@href",   # Attribute extraction with @
    "image": "img@src"          # Any attribute: @src, @href, @alt, etc.
}

# Extract data - no manual loops, no site-specific logic
products = rusticsoup.extract_data(html, "div.product", field_mappings)

print(products)
# [{"title": "Amazing Product", "price": "$29.99", "link": "/buy", "image": "/image.jpg"}]
```

## 🎯 Core Features

### 🌟 NEW: WebPage API (web-poet inspired)

High-level, declarative API for web scraping:

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://example.com")

# Simple extraction
title = page.text("h1")
links = page.attr_all("a", "href")

# Extract multiple items at once
products = page.extract_all(".product", {
    "name": "h2",
    "price": ".price",
    "url": "a@href"
})

# Check existence
if page.has("nav.menu"):
    nav_items = page.text_all("nav.menu a")

# URL resolution
absolute_url = page.absolute_url("/products/123")
```

**[📖 Full WebPage API Documentation](WEBPAGE_API.md)** | **[🚀 Quick Start Guide](WEBPAGE_QUICKSTART.md)**

### ✅ Universal Extraction
Works with **any HTML structure** - no site-specific parsers needed:

```python
# Google Shopping
rusticsoup.extract_data(html, 'tr[data-is-grid-offer="true"]', {
    'seller': 'a.b5ycib',
    'price': 'span.g9WBQb',
    'link': 'a.UxuaJe@href'
})

# Amazon Products
rusticsoup.extract_data(html, '[data-component-type="s-search-result"]', {
    'title': 'h2 a span',
    'price': '.a-price-whole',
    'rating': '.a-icon-alt',
    'url': 'h2 a@href'
})

# Any website
rusticsoup.extract_data(html, 'your-container-selector', {
    'any_field': 'any.css.selector',
    'any_attribute': 'element@attribute_name'
})
```

### ✅ Bulk Processing
Process multiple pages in parallel:

```python
# Process 100 pages simultaneously
pages = [html1, html2, html3, ...]  # List of HTML strings
results = rusticsoup.extract_data_bulk(pages, "div.product", field_mappings)

# Each page processed in parallel using Rust's Rayon
# 10-100x faster than sequential processing
```

### ✅ Attribute Extraction
No more manual loops for getting href, src, etc:

```python
# Before (BeautifulSoup)
links = []
for element in soup.select('a'):
    if element.get('href'):
        links.append(element['href'])

# After (RusticSoup)
data = rusticsoup.extract_data(html, 'div', {'links': 'a@href'})
```

### ✅ Browser-Grade Parsing
Built on **html5ever** - the same HTML parser used by Firefox and Servo:
- Handles malformed HTML perfectly
- WHATWG HTML5 compliant
- Blazing fast C-level performance
- Memory safe (Rust)

## 📊 Performance Benchmarks

Real-world scraping performance vs BeautifulSoup:

```python
# Google Shopping: 30 ads per page
BeautifulSoup:  8.1ms per page
RusticSoup:     3.9ms per page  (2.1x faster)

# Product grids: 50 products per page
BeautifulSoup:  14ms per page
RusticSoup:     1.2ms per page  (12x faster)

# Bulk processing: 100 pages
BeautifulSoup:  Sequential ~1.4s
RusticSoup:     Parallel ~14ms   (100x faster)
```

## 🛠️ API Reference

### Two Powerful APIs

RusticSoup provides two complementary APIs:

1. **[WebPage API](WEBPAGE_API.md)** - High-level, object-oriented (Recommended for new projects)
2. **Universal Extraction API** - Function-based, great for batch processing

### WebPage API

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://example.com")
```

**Key Methods:**
- `text(selector)` - Extract text from first match
- `text_all(selector)` - Extract text from all matches
- `attr(selector, attribute)` - Extract attribute from first match
- `attr_all(selector, attribute)` - Extract attribute from all matches
- `extract(mappings)` - Extract structured data
- `extract_all(container, mappings)` - Extract multiple items
- `has(selector)` - Check if selector matches
- `count(selector)` - Count matching elements
- `absolute_url(url)` - Convert relative to absolute URL

**[📖 Full WebPage Documentation](WEBPAGE_API.md)**

### 🔄 Field Transforms (NEW in v0.2.2)

Apply transformations to extracted data automatically:

```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

class Article(ItemPage):
    # Single transform
    title = Field(css="h1", transform=str.upper)

    # Chain multiple transforms
    author = Field(
        css=".author",
        transform=[
            str.strip,
            str.title,
            lambda s: s.replace("by ", "")
        ]
    )

    # Transform with attribute extraction
    price = Field(
        css=".price",
        transform=[
            str.strip,
            lambda s: float(s.replace("$", ""))
        ]
    )

    # Transform lists
    tags = Field(
        css=".tag",
        get_all=True,
        transform=lambda tags: [t.upper() for t in tags]
    )

page = WebPage(html)
article = Article(page)

print(article.title)   # "UNDERSTANDING RUST"
print(article.author)  # "Jane Smith"
print(article.price)   # 19.99
print(article.tags)    # ["PYTHON", "RUST", "WEB"]
```

**Benefits:**
- ✅ No manual post-processing needed
- ✅ Clean, declarative field definitions
- ✅ Reusable transform functions
- ✅ Chain multiple transforms in order
- ✅ Works with single values, lists, and attributes

**[📖 Full Transform Documentation](FIELD_TRANSFORM.md)**

### Universal Extraction API

#### `extract_data(html, container_selector, field_mappings)`
Universal HTML data extraction - works with any website structure.

**Parameters:**
- `html`: HTML string to parse
- `container_selector`: CSS selector for container elements
- `field_mappings`: Dict mapping field names to CSS selectors

**Returns:** List of dictionaries with extracted data

#### `extract_data_bulk(html_pages, container_selector, field_mappings)`
Parallel processing of multiple HTML pages.

**Parameters:**
- `html_pages`: List of HTML strings
- `container_selector`: CSS selector for container elements
- `field_mappings`: Dict mapping field names to CSS selectors

**Returns:** List of lists - one result list per input page

#### `parse_html(html)`
Low-level HTML parsing - returns WebScraper object for manual DOM traversal.

**Parameters:**
- `html`: HTML string to parse

**Returns:** WebScraper object with select(), text(), attr() methods

### Selector Syntax

| Syntax | Description | Example |
|--------|-------------|---------|
| `"selector"` | Extract text content | `"h1"` → "Page Title" |
| `"selector@attr"` | Extract attribute | `"a@href"` → "/page.html" |
| `"selector@get_all"` | Extract all text | `"p@get_all"` → ["P1", "P2"] |
| `"complex selector"` | Any CSS selector | `"div.class > p:first-child"` |

### Supported Attributes
Any HTML attribute: `@href`, `@src`, `@alt`, `@class`, `@id`, `@data-*`, etc.

## 🏗️ Advanced Usage

### Custom Processing
```python
# Extract data then post-process
ads = rusticsoup.extract_data(html, "tr.ad", {
    "price": "span.price",
    "link": "a@href"
})

# Post-process the results
for ad in ads:
    # Clean price: "$29.99" → 29.99
    ad["price"] = float(ad["price"].replace("$", ""))

    # Convert relative URLs to absolute
    if ad["link"].startswith("/"):
        ad["link"] = f"https://example.com{ad['link']}"
```

### Table Extraction
```python
# Extract HTML tables easily
table_data = rusticsoup.extract_table_data(html, "table.data")
# Returns: [["Header1", "Header2"], ["Row1Col1", "Row1Col2"], ...]
```

### Error Handling
```python
try:
    data = rusticsoup.extract_data(html, "div.product", field_mappings)
except Exception as e:
    print(f"Parsing error: {e}")
    data = []
```

## 🆚 Migration from BeautifulSoup

### Option 1: WebPage API (Recommended)

```python
# BeautifulSoup - Imperative, verbose
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'html.parser')
products = []

for product in soup.select('div.product'):
    title = product.select_one('h2')
    price = product.select_one('span.price')
    link = product.select_one('a')

    products.append({
        'title': title.text if title else '',
        'price': price.text if price else '',
        'link': link.get('href') if link else ''
    })

# RusticSoup WebPage - Declarative, concise
from rusticsoup import WebPage

page = WebPage(html)
products = page.extract_all('div.product', {
    'title': 'h2',
    'price': 'span.price',
    'link': 'a@href'
})
```

### Option 2: Universal Extraction API

```python
# RusticSoup Universal API - Function-based
import rusticsoup

products = rusticsoup.extract_data(html, 'div.product', {
    'title': 'h2',
    'price': 'span.price',
    'link': 'a@href'
})
```

**90% less code, 2-10x faster, handles attributes automatically!**

### web-poet to RusticSoup

RusticSoup's WebPage API is compatible with web-poet patterns:

```python
# web-poet (async, slower)
from web_poet import WebPage

async def parse(page: WebPage):
    title = await page.css("h1::text").get()
    links = await page.css("a::attr(href)").getall()
    return {"title": title, "links": links}

# RusticSoup WebPage (sync, faster - no async needed!)
from rusticsoup import WebPage

def parse(html: str):
    page = WebPage(html)
    title = page.text("h1")
    links = page.attr_all("a", "href")
    return {"title": title, "links": links}
```

## 🔧 Installation

### From PyPI (Recommended)
```bash
pip install rusticsoup
```

### From Source
```bash
# Requires Rust toolchain
git clone https://github.com/yourusername/rusticsoup
cd rusticsoup
maturin develop --release
```

### System Requirements
- Python 3.11+
- No additional dependencies (self-contained)

## 📈 Use Cases

Perfect for:
- **Web scraping** - Extract data from any website
- **Data mining** - Process large amounts of HTML
- **Price monitoring** - Track e-commerce prices
- **Content aggregation** - Collect articles, posts, listings
- **SEO analysis** - Extract meta tags, titles, links
- **API alternatives** - Scrape when no API exists

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on [html5ever](https://github.com/servo/html5ever) - Mozilla's HTML5 parser
- Powered by [scraper](https://github.com/causal-agent/scraper) - CSS selector support
- Inspired by [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - the original HTML parsing library
- WebPage API inspired by [web-poet](https://github.com/scrapinghub/web-poet) - declarative web scraping

---

**Made with 🦀 and ❤️ - RusticSoup: Where Rust meets HTML parsing perfection**
