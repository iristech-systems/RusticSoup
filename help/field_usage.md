# Field Usage Guide

The `Field` class in RusticSoup provides declarative field descriptors for building reusable extraction patterns. Think of Fields as extraction templates that you can define once and reuse across multiple pages.

## Quick Start

```python
from rusticsoup import WebPage, Field

# Define reusable field extractors
title_field = Field(css="h1")
author_field = Field(css=".author")
link_field = Field(css="a", attr="href")
tags_field = Field(css=".tag", get_all=True)

# Use on any page
page = WebPage(html)
title = title_field.extract(page)
tags = tags_field.extract(page)
```

## Why Use Fields?

### Reusability
Define extraction patterns once, use everywhere:

```python
# Define fields once
price_field = Field(css=".price")
rating_field = Field(css=".rating")

# Use on multiple pages
product1_price = price_field.extract(page1)
product2_price = price_field.extract(page2)
product3_price = price_field.extract(page3)
```

### Declarative
Clear, self-documenting extraction logic:

```python
# Clear what each field extracts
product_fields = {
    "title": Field(css="h2.product-title"),
    "price": Field(css="span.price"),
    "image": Field(css="img.product-image", attr="src"),
    "tags": Field(css=".tag", get_all=True)
}
```

### Library Building
Perfect for building extraction libraries:

```python
# amazon_extractors.py
class AmazonFields:
    title = Field(css="span#productTitle")
    price = Field(css="span.a-price-whole")
    rating = Field(css="span.a-icon-alt")
    images = Field(css="img.a-dynamic-image", attr="src", get_all=True)

# Use in your scraper
from amazon_extractors import AmazonFields
page = WebPage(html)
title = AmazonFields.title.extract(page)
```

## Field Options

```python
Field(
    css=None,        # CSS selector
    xpath=None,      # XPath selector (not yet implemented)
    attr=None,       # Attribute to extract (e.g., "href", "src")
    get_all=False,   # Extract from all matching elements
    default=None,    # Default value if not found (not yet used)
    required=True    # Whether field is required (not yet used)
)
```

## Examples

### Text Extraction

```python
from rusticsoup import WebPage, Field

html = """
<article>
    <h1>Article Title</h1>
    <p class="lead">Lead paragraph...</p>
</article>
"""

page = WebPage(html)

# Extract text
title_field = Field(css="h1")
lead_field = Field(css="p.lead")

title = title_field.extract(page)  # "Article Title"
lead = lead_field.extract(page)    # "Lead paragraph..."
```

### Attribute Extraction

```python
html = """
<div class="product">
    <a href="/products/123">View Product</a>
    <img src="/images/product.jpg" alt="Product">
</div>
"""

page = WebPage(html)

# Extract attributes
link_field = Field(css="a", attr="href")
image_field = Field(css="img", attr="src")
alt_field = Field(css="img", attr="alt")

link = link_field.extract(page)    # "/products/123"
image = image_field.extract(page)  # "/images/product.jpg"
alt = alt_field.extract(page)      # "Product"
```

### Multiple Items (get_all=True)

```python
html = """
<article>
    <p>First paragraph</p>
    <p>Second paragraph</p>
    <p>Third paragraph</p>
    <span class="tag">Python</span>
    <span class="tag">Rust</span>
    <span class="tag">Web</span>
</article>
"""

page = WebPage(html)

# Extract all matching elements
paragraphs_field = Field(css="p", get_all=True)
tags_field = Field(css=".tag", get_all=True)

paragraphs = paragraphs_field.extract(page)
# ['First paragraph', 'Second paragraph', 'Third paragraph']

tags = tags_field.extract(page)
# ['Python', 'Rust', 'Web']
```

### Reusable Extraction Patterns

```python
# Define fields for a specific site structure
class BlogFields:
    title = Field(css="h1.post-title")
    author = Field(css=".author-name")
    date = Field(css="time", attr="datetime")
    content = Field(css=".post-content p", get_all=True)
    tags = Field(css=".tag a", get_all=True)

# Use on multiple blog posts
post1 = WebPage(html1)
post2 = WebPage(html2)

# Same fields work on all posts
title1 = BlogFields.title.extract(post1)
title2 = BlogFields.title.extract(post2)

tags1 = BlogFields.tags.extract(post1)
tags2 = BlogFields.tags.extract(post2)
```

## Field vs WebPage Methods

Both approaches work - choose based on your needs:

### WebPage Methods (Direct)
Good for quick, one-off extractions:

```python
page = WebPage(html)

# Direct extraction
title = page.text("h1")
link = page.attr("a", "href")
tags = page.text_all(".tag")
```

When to use:
- Quick scripts
- One-time extractions
- Prefer functional style

### Field Objects (Declarative)
Good for reusable patterns:

```python
# Define once
title_field = Field(css="h1")
link_field = Field(css="a", attr="href")
tags_field = Field(css=".tag", get_all=True)

# Use many times
title = title_field.extract(page1)
title = title_field.extract(page2)
title = title_field.extract(page3)
```

When to use:
- Reusable extraction patterns
- Building extraction libraries
- Declarative field definitions
- Team collaboration (clear contracts)

## Real-World Example

```python
from rusticsoup import WebPage, Field

# Define extraction fields for an e-commerce site
class ProductFields:
    """Reusable extractors for product pages"""

    # Basic info
    title = Field(css="h1.product-title")
    description = Field(css=".product-description")

    # Pricing
    current_price = Field(css=".current-price")
    original_price = Field(css=".original-price")

    # Media
    main_image = Field(css="img.main-image", attr="src")
    all_images = Field(css="img.gallery-image", attr="src", get_all=True)

    # Metadata
    brand = Field(css=".brand-name")
    sku = Field(css="span[data-sku]", attr="data-sku")

    # Social
    rating = Field(css=".rating-value")
    review_count = Field(css=".review-count")

    # Categories
    categories = Field(css=".breadcrumb a", get_all=True)
    tags = Field(css=".tag", get_all=True)

# Use the fields
page = WebPage(html, url="https://shop.example.com/product/123")

# Extract product data
product = {
    "title": ProductFields.title.extract(page),
    "description": ProductFields.description.extract(page),
    "current_price": ProductFields.current_price.extract(page),
    "original_price": ProductFields.original_price.extract(page),
    "main_image": ProductFields.main_image.extract(page),
    "all_images": ProductFields.all_images.extract(page),
    "brand": ProductFields.brand.extract(page),
    "sku": ProductFields.sku.extract(page),
    "rating": ProductFields.rating.extract(page),
    "review_count": ProductFields.review_count.extract(page),
    "categories": ProductFields.categories.extract(page),
    "tags": ProductFields.tags.extract(page),
}

print(product)
```

## Building an Extraction Library

```python
# extractors/amazon.py
from rusticsoup import Field

class AmazonProductFields:
    title = Field(css="span#productTitle")
    price = Field(css="span.a-price-whole")
    currency = Field(css="span.a-price-symbol")
    rating = Field(css="span.a-icon-alt")
    rating_count = Field(css="span#acrCustomerReviewText")
    availability = Field(css="div#availability span")
    images = Field(css="img.a-dynamic-image", attr="src", get_all=True)
    features = Field(css="div#feature-bullets li span", get_all=True)


# extractors/ebay.py
class EbayProductFields:
    title = Field(css="h1.x-item-title__mainTitle")
    price = Field(css="div.x-price-primary span")
    condition = Field(css="div.x-item-condition-text span")
    watchers = Field(css="span.watchers")
    bids = Field(css="span.bids")
    images = Field(css="div.ux-image-carousel img", attr="src", get_all=True)


# scraper.py
from rusticsoup import WebPage
from extractors.amazon import AmazonProductFields
from extractors.ebay import EbayProductFields

def scrape_amazon(html):
    page = WebPage(html)
    return {
        "title": AmazonProductFields.title.extract(page),
        "price": AmazonProductFields.price.extract(page),
        "rating": AmazonProductFields.rating.extract(page),
        "features": AmazonProductFields.features.extract(page),
    }

def scrape_ebay(html):
    page = WebPage(html)
    return {
        "title": EbayProductFields.title.extract(page),
        "price": EbayProductFields.price.extract(page),
        "condition": EbayProductFields.condition.extract(page),
        "images": EbayProductFields.images.extract(page),
    }
```

## Tips & Best Practices

### 1. Name Fields Descriptively
```python
# Good
product_title_field = Field(css="h1.product-title")
author_name_field = Field(css=".author-name")

# Less clear
field1 = Field(css="h1.product-title")
f = Field(css=".author-name")
```

### 2. Group Related Fields
```python
class ArticleFields:
    # Metadata
    title = Field(css="h1")
    author = Field(css=".author")
    date = Field(css="time", attr="datetime")

    # Content
    lead = Field(css=".lead-paragraph")
    body = Field(css=".article-body p", get_all=True)

    # Media
    main_image = Field(css=".hero-image", attr="src")
    gallery = Field(css=".gallery img", attr="src", get_all=True)
```

### 3. Document Field Purpose
```python
class ProductFields:
    """Field extractors for e-commerce product pages"""

    # Primary product identifier
    sku = Field(css="span[data-sku]", attr="data-sku")

    # Display price (may include formatting)
    display_price = Field(css=".price")

    # All available colors
    colors = Field(css=".color-option", attr="data-color", get_all=True)
```

### 4. Handle Missing Data
```python
page = WebPage(html)

# Fields return None for missing elements
price = price_field.extract(page)
if price is None:
    price = "Price not available"

# Or provide defaults
display_price = price or "Contact for price"
```

## Future Enhancements

Planned features for Field class:

- [ ] `default` parameter support (fallback values)
- [ ] `required` parameter validation
- [ ] XPath selector support
- [ ] Custom transformation functions
- [ ] Nested field extraction
- [ ] Field validation and type conversion

## See Also
- WebPage API Documentation: ./webpage_api.md
- Quick Start Guide: ./quickstart.md
- Fallback Selectors Guide: ./fallback_selectors.md
- ItemPage: Containers + Mapping: ./itempage_containers.md
- Test Suite (examples): ../../test_field_usage.py
