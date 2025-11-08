# PageObject Pattern - Auto-Extraction with RusticSoup

The PageObject pattern allows you to define Fields once and auto-extract when instantiated. This is the web-poet inspired pattern where you build page classes with Field descriptors, and extraction happens automatically.

## Quick Start

```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

# Define your page structure
class Product(ItemPage):
    title = Field(css="h1.product-title")
    price = Field(css=".price")
    images = Field(css="img.product", attr="src", get_all=True)

# Auto-extract!
page = WebPage(html)
product = Product(page)

# Access extracted data
print(product.title)   # "Amazing Widget"
print(product.price)   # "$99.99"
print(product.images)  # ["/img1.jpg", "/img2.jpg"]
```

That's it! Fields are extracted automatically on instantiation.

## Why Use PageObject Pattern?

### Declarative
Define what you want to extract, not how:

```python
class Article(ItemPage):
    title = Field(css="h1")
    author = Field(css=".author")
    date = Field(css="time", attr="datetime")
    tags = Field(css=".tag", get_all=True)
```

### Reusable
Define once, use on many pages:

```python
# Define once
class BlogPost(ItemPage):
    title = Field(css="h1.post-title")
    author = Field(css=".author")

# Use on multiple pages
post1 = BlogPost(WebPage(html1))
post2 = BlogPost(WebPage(html2))
post3 = BlogPost(WebPage(html3))
```

### Clean API
Access fields as attributes:

```python
product = Product(page)
print(product.title)  # Not product.extract('title')!
```

### Type-Safe (with type hints)

```python
class Product(ItemPage):
    title: str = Field(css="h1")
    price: str = Field(css=".price")
    images: list[str] = Field(css="img", attr="src", get_all=True)
```

## Installation

The PageObject pattern requires the `rusticsoup_helpers` module:

```python
# Make sure rusticsoup_helpers.py is in your project
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage
```

## Basic Usage

### 1. Define Page Class

```python
from rusticsoup_helpers import ItemPage
from rusticsoup import Field

class ProductPage(ItemPage):
    # Text fields
    title = Field(css="h1.product-title")
    description = Field(css=".description")

    # Attribute fields
    main_image = Field(css="img.main", attr="src")

    # Multiple items
    all_images = Field(css="img.gallery", attr="src", get_all=True)
    features = Field(css=".feature-item", get_all=True)
```

### 2. Create Instance

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://example.com/product")
product = ProductPage(page)  # Auto-extraction happens here!
```

### 3. Access Data

```python
# Access as attributes
print(product.title)
print(product.description)
print(product.main_image)
print(len(product.all_images))

# Convert to dict
data = product.to_dict()
print(data)
# {'title': '...', 'description': '...', 'main_image': '...', ...}
```

## Complete Example

```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

# Define page structure
class AmazonProduct(ItemPage):
    """Auto-extracting page object for Amazon product pages"""

    # Basic info
    title = Field(css="span#productTitle")
    brand = Field(css="#bylineInfo")

    # Pricing
    price = Field(css="span.a-price-whole")
    currency = Field(css="span.a-price-symbol")

    # Social proof
    rating = Field(css="span.a-icon-alt")
    review_count = Field(css="span#acrCustomerReviewText")

    # Availability
    availability = Field(css="#availability span")

    # Media
    images = Field(css="img.a-dynamic-image", attr="src", get_all=True)

    # Features
    features = Field(css="#feature-bullets li span", get_all=True)

# HTML from Amazon
html = """
<div class="product">
    <span id="productTitle">Bluetooth Wireless Mouse</span>
    <span id="bylineInfo">Brand: LogiTech</span>
    <span class="a-price-whole">29</span>
    <span class="a-price-symbol">$</span>
    <span class="a-icon-alt">4.5 out of 5 stars</span>
    <span id="acrCustomerReviewText">2,547 ratings</span>
    <div id="availability"><span>In Stock</span></div>
    <img class="a-dynamic-image" src="/images/mouse1.jpg">
    <img class="a-dynamic-image" src="/images/mouse2.jpg">
    <div id="feature-bullets">
        <ul>
            <li><span>Wireless connectivity</span></li>
            <li><span>Ergonomic design</span></li>
        </ul>
    </div>
</div>
"""

# Auto-extract
page = WebPage(html)
product = AmazonProduct(page)

# Use the data
print(f"Product: {product.title}")
print(f"Brand: {product.brand}")
print(f"Price: {product.currency}{product.price}")
print(f"Rating: {product.rating} ({product.review_count})")
print(f"Available: {product.availability}")
print(f"\nFeatures:")
for feature in product.features:
    print(f"  • {feature}")
print(f"\nImages: {len(product.images)} available")

# Convert to dict for storage/API
product_data = product.to_dict()
```

## Real-World Examples

### E-commerce Scraper

```python
class ProductPage(ItemPage):
    # Product info
    name = Field(css="h1.product-name")
    sku = Field(css="span.sku")
    brand = Field(css=".brand-name")

    # Pricing
    current_price = Field(css=".current-price")
    original_price = Field(css=".original-price")
    discount = Field(css=".discount-percent")

    # Description
    short_desc = Field(css=".short-description")
    long_desc = Field(css=".long-description")

    # Media
    main_image = Field(css="img.main-image", attr="src")
    gallery_images = Field(css="img.gallery-thumb", attr="src", get_all=True)

    # Reviews
    rating = Field(css=".rating-value")
    review_count = Field(css=".review-count")

    # Inventory
    in_stock = Field(css=".availability")
    ships_in = Field(css=".shipping-time")

    # Categories
    categories = Field(css=".breadcrumb a", get_all=True)
    tags = Field(css=".product-tag", get_all=True)

# Use it
page = WebPage(html, url="https://shop.example.com/product/123")
product = ProductPage(page)

# All fields auto-extracted!
print(f"{product.name} by {product.brand}")
print(f"Price: {product.current_price} (was {product.original_price})")
print(f"Rating: {product.rating} ({product.review_count} reviews)")
```

### Blog Post Scraper

```python
class BlogPost(ItemPage):
    # Metadata
    title = Field(css="h1.post-title")
    author = Field(css=".author-name")
    author_url = Field(css=".author-link", attr="href")
    publish_date = Field(css="time", attr="datetime")
    category = Field(css=".post-category")

    # Content
    excerpt = Field(css=".post-excerpt")
    body_paragraphs = Field(css=".post-body p", get_all=True)

    # Media
    hero_image = Field(css=".hero-image", attr="src")
    hero_alt = Field(css=".hero-image", attr="alt")

    # Taxonomy
    tags = Field(css=".tag-link", get_all=True)
    tag_urls = Field(css=".tag-link", attr="href", get_all=True)

    # Engagement
    view_count = Field(css=".view-count")
    comment_count = Field(css=".comment-count")
    share_count = Field(css=".share-count")

# Scrape multiple posts
posts = []
for url in blog_urls:
    html = fetch_url(url)
    page = WebPage(html, url=url)
    post = BlogPost(page)
    posts.append(post.to_dict())

# Save to database
save_to_db(posts)
```

### Job Listing Scraper

```python
class JobListing(ItemPage):
    # Job details
    title = Field(css="h1.job-title")
    company = Field(css=".company-name")
    company_url = Field(css=".company-link", attr="href")
    location = Field(css=".job-location")
    job_type = Field(css=".job-type")  # Full-time, Part-time, etc.

    # Compensation
    salary_range = Field(css=".salary-range")
    benefits = Field(css=".benefit-item", get_all=True)

    # Description
    summary = Field(css=".job-summary")
    responsibilities = Field(css=".responsibilities li", get_all=True)
    requirements = Field(css=".requirements li", get_all=True)

    # Application
    apply_url = Field(css=".apply-button", attr="href")
    posted_date = Field(css=".posted-date", attr="datetime")
    deadline = Field(css=".application-deadline", attr="datetime")

    # Company info
    company_size = Field(css=".company-size")
    industry = Field(css=".industry")

page = WebPage(html)
job = JobListing(page)

print(f"{job.title} at {job.company}")
print(f"Location: {job.location}")
print(f"Type: {job.job_type}")
print(f"Salary: {job.salary_range}")
print(f"\nResponsibilities:")
for resp in job.responsibilities:
    print(f"  • {resp}")
```

## Advanced Patterns

### Reusable Field Collections

```python
# shared_fields.py
from rusticsoup import Field

class PricingFields:
    """Reusable pricing fields"""
    current_price = Field(css=".current-price")
    original_price = Field(css=".original-price")
    discount = Field(css=".discount")
    currency = Field(css=".currency")

class RatingFields:
    """Reusable rating fields"""
    rating = Field(css=".rating-value")
    rating_count = Field(css=".rating-count")
    review_count = Field(css=".review-count")

# product.py
from rusticsoup_helpers import ItemPage
from shared_fields import PricingFields, RatingFields

class Product(ItemPage, PricingFields, RatingFields):
    title = Field(css="h1")
    description = Field(css=".description")
    # Pricing and rating fields inherited!
```

### Nested Extraction

```python
class ProductWithReviews(ItemPage):
    # Product fields
    title = Field(css="h1.product-title")
    price = Field(css=".price")

    # Review fields (extract all reviews)
    reviewer_names = Field(css=".review .reviewer-name", get_all=True)
    review_ratings = Field(css=".review .rating", get_all=True)
    review_texts = Field(css=".review .text", get_all=True)
    review_dates = Field(css=".review .date", attr="datetime", get_all=True)

page = WebPage(html)
product = ProductWithReviews(page)

# Zip reviews together
reviews = list(zip(
    product.reviewer_names,
    product.review_ratings,
    product.review_texts,
    product.review_dates
))

for name, rating, text, date in reviews:
    print(f"{name} ({rating}) - {date}")
    print(f"  {text}")
```

### Building Extraction Libraries

```python
# extractors/amazon.py
from rusticsoup_helpers import ItemPage
from rusticsoup import Field

class AmazonProduct(ItemPage):
    title = Field(css="span#productTitle")
    price = Field(css="span.a-price-whole")
    # ... more fields

class AmazonSearch(ItemPage):
    product_titles = Field(css="h2.s-line-clamp-2", get_all=True)
    product_urls = Field(css="h2.s-line-clamp-2 a", attr="href", get_all=True)
    # ... more fields

# extractors/ebay.py
class EbayProduct(ItemPage):
    title = Field(css="h1.x-item-title__mainTitle")
    price = Field(css="div.x-price-primary span")
    # ... more fields

# scraper.py
from extractors.amazon import AmazonProduct
from extractors.ebay import EbayProduct

def scrape_amazon(html):
    page = WebPage(html)
    return AmazonProduct(page).to_dict()

def scrape_ebay(html):
    page = WebPage(html)
    return EbayProduct(page).to_dict()
```

## API Reference

### ItemPage

Base class for page objects with auto-extraction.

```python
class ItemPage(metaclass=PageObjectMeta):
    def __init__(self, page: WebPage)
    def to_dict(self) -> dict
```

Usage:

```python
class MyPage(ItemPage):
    field1 = Field(css="selector1")
    field2 = Field(css="selector2")

page = WebPage(html)
obj = MyPage(page)
print(obj.field1)  # Auto-extracted
```

### @page_object Decorator

Decorator for creating page objects (alternative to ItemPage).

```python
from rusticsoup_helpers import page_object

@page_object
class Product:
    title = Field(css="h1")
    price = Field(css=".price")

page = WebPage(html)
product = Product(page)
print(product.title)  # Auto-extracted
```

## Tips & Best Practices

1. Organize Fields by Purpose
2. Use Type Hints
3. Document Field Purposes
4. Handle Missing Data
5. Validate After Extraction

## Comparison with Other Approaches

### PageObject vs Direct Extraction

```python
# PageObject (best for reusable extraction)
class Product(ItemPage):
    title = Field(css="h1")
    price = Field(css=".price")

product = Product(WebPage(html))
print(product.title)

# Direct WebPage (best for one-off extraction)
page = WebPage(html)
title = page.text("h1")
price = page.text(".price")

# Manual Fields (best for custom logic)
title_field = Field(css="h1")
title = title_field.extract(WebPage(html))
```

When to use PageObject:
- Reusable extraction across many pages
- Building extraction libraries
- Team collaboration (clear contracts)
- Complex data structures
- Need validation/post-processing

## Future Enhancements

Planned features:
- Nested PageObject support
- Field validation decorators
- Custom field types
- Lazy field extraction
- Caching extracted values

## See Also

- Field Usage Guide: ./field_usage.md
- WebPage API: ./webpage_api.md
- Test Examples: ../../test_page_object_pattern.py
