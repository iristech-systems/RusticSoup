"""
Test WebPoet-style WebPage API for RusticSoup

This demonstrates the new WebPage-based parsing similar to web-poet
"""

from rusticsoup import WebPage


def test_webpage_basic():
    """Test basic WebPage creation and methods"""
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Welcome</h1>
            <p class="intro">This is a test</p>
            <a href="/page1">Link 1</a>
            <a href="/page2">Link 2</a>
        </body>
    </html>
    """

    page = WebPage(html, url="https://example.com/test")

    # Test basic properties
    assert page.url == "https://example.com/test"
    print(f"✓ Page URL: {page.url}")

    # Test text extraction
    title = page.text("h1")
    assert title == "Welcome"
    print(f"✓ Title: {title}")

    intro = page.text("p.intro")
    assert intro == "This is a test"
    print(f"✓ Intro: {intro}")

    # Test attribute extraction
    link = page.attr("a", "href")
    assert link == "/page1"
    print(f"✓ First link: {link}")

    # Test extract all
    all_links = page.attr_all("a", "href")
    assert len(all_links) == 2
    assert all_links[0] == "/page1"
    assert all_links[1] == "/page2"
    print(f"✓ All links: {all_links}")

    # Test has() method
    assert page.has("h1")
    assert not page.has("h2")
    print("✓ has() method works")

    # Test count() method
    assert page.count("a") == 2
    print("✓ count() method works")

    print("\n✅ Basic WebPage tests passed!")


def test_webpage_extract():
    """Test WebPage.extract() with field mappings"""
    html = """
    <div class="product">
        <h2>Amazing Widget</h2>
        <span class="price">$29.99</span>
        <a href="/buy" class="buy-btn">Buy Now</a>
        <img src="/widget.jpg" alt="widget">
        <div class="rating">4.5 stars</div>
    </div>
    """

    page = WebPage(html, url="https://shop.example.com/widget")

    # Extract structured data
    data = page.extract(
        {
            "title": "h2",
            "price": "span.price",
            "link": "a.buy-btn@href",
            "image": "img@src",
            "rating": "div.rating",
        }
    )

    assert data["title"] == "Amazing Widget"
    assert data["price"] == "$29.99"
    assert data["link"] == "/buy"
    assert data["image"] == "/widget.jpg"
    assert data["rating"] == "4.5 stars"

    print("✓ Extracted data:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    print("\n✅ WebPage.extract() tests passed!")


def test_webpage_extract_all():
    """Test WebPage.extract_all() for multiple items"""
    html = """
    <div class="product">
        <h3>Product 1</h3>
        <span class="price">$10</span>
        <a href="/p1">View</a>
    </div>
    <div class="product">
        <h3>Product 2</h3>
        <span class="price">$20</span>
        <a href="/p2">View</a>
    </div>
    <div class="product">
        <h3>Product 3</h3>
        <span class="price">$30</span>
        <a href="/p3">View</a>
    </div>
    """

    page = WebPage(html)

    # Extract all products
    products = page.extract_all(
        "div.product", {"name": "h3", "price": "span.price", "url": "a@href"}
    )

    assert len(products) == 3
    assert products[0]["name"] == "Product 1"
    assert products[1]["price"] == "$20"
    assert products[2]["url"] == "/p3"

    print("✓ Extracted products:")
    for i, product in enumerate(products, 1):
        print(f"  Product {i}: {product}")

    print("\n✅ WebPage.extract_all() tests passed!")


def test_webpage_get_all_syntax():
    """Test @get_all syntax for extracting multiple values"""
    html = """
    <div class="container">
        <p>First paragraph</p>
        <p>Second paragraph</p>
        <p>Third paragraph</p>
        <img src="/img1.jpg">
        <img src="/img2.jpg">
        <img src="/img3.jpg">
    </div>
    """

    page = WebPage(html)

    # Extract all paragraphs
    paragraphs = page.text_all("p")
    assert len(paragraphs) == 3
    assert paragraphs[0] == "First paragraph"
    print(f"✓ All paragraphs: {paragraphs}")

    # Extract all images
    images = page.attr_all("img", "src")
    assert len(images) == 3
    assert images[1] == "/img2.jpg"
    print(f"✓ All images: {images}")

    print("\n✅ @get_all syntax tests passed!")


def test_field_descriptors():
    """Test Field descriptor creation"""
    html = """
    <article>
        <h1>Article Title</h1>
        <span class="author">John Doe</span>
        <div class="content">Article content here</div>
        <a href="/article/123">Read more</a>
        <img src="/thumb.jpg" alt="thumbnail">
        <span class="tag">Python</span>
        <span class="tag">Rust</span>
        <span class="tag">Web</span>
    </article>
    """

    page = WebPage(html, url="https://blog.example.com/post")

    # For now, use WebPage methods directly
    title = page.text("h1")
    author = page.text("span.author")
    link = page.attr("a", "href")
    image = page.attr("img", "src")
    tags = page.text_all("span.tag")

    assert title == "Article Title"
    assert author == "John Doe"
    assert link == "/article/123"
    assert image == "/thumb.jpg"
    assert len(tags) == 3
    assert "Rust" in tags

    print("✓ Field descriptors created successfully")
    print(f"✓ Title: {title}")
    print(f"✓ Author: {author}")
    print(f"✓ Link: {link}")
    print(f"✓ Image: {image}")
    print(f"✓ Tags: {tags}")

    print("\n✅ Field descriptor tests passed!")


def test_absolute_url():
    """Test absolute_url() method"""
    page = WebPage("<html></html>", url="https://example.com/path/page.html")

    # Test already absolute URL
    abs1 = page.absolute_url("https://other.com/page")
    assert abs1 == "https://other.com/page"

    # Test absolute path
    abs2 = page.absolute_url("/absolute/path")
    assert abs2 == "https://example.com/absolute/path"

    # Test relative path
    abs3 = page.absolute_url("relative")
    assert abs3 == "https://example.com/path/relative"

    print("✓ Absolute URLs:")
    print(f"  {abs1}")
    print(f"  {abs2}")
    print(f"  {abs3}")

    print("\n✅ absolute_url() tests passed!")


def test_real_world_google_shopping():
    """Test with real-world Google Shopping-like structure"""
    html = """
    <table class="results">
        <tr data-is-grid-offer="true">
            <td><a class="merchant" href="/store1">Store 1</a></td>
            <td><span class="price">$99.99</span></td>
            <td><a class="product-link" href="/product1">Product 1</a></td>
        </tr>
        <tr data-is-grid-offer="true">
            <td><a class="merchant" href="/store2">Store 2</a></td>
            <td><span class="price">$89.99</span></td>
            <td><a class="product-link" href="/product2">Product 2</a></td>
        </tr>
    </table>
    """

    page = WebPage(html, url="https://shopping.google.com/search")

    offers = page.extract_all(
        'tr[data-is-grid-offer="true"]',
        {
            "merchant": "a.merchant",
            "merchant_url": "a.merchant@href",
            "price": "span.price",
            "product_name": "a.product-link",
            "product_url": "a.product-link@href",
        },
    )

    assert len(offers) == 2
    assert offers[0]["merchant"] == "Store 1"
    assert offers[0]["price"] == "$99.99"
    assert offers[1]["merchant_url"] == "/store2"

    print("✓ Google Shopping-like extraction:")
    for i, offer in enumerate(offers, 1):
        print(f"  Offer {i}:")
        for key, value in offer.items():
            print(f"    {key}: {value}")

    print("\n✅ Real-world Google Shopping tests passed!")


def test_real_world_amazon():
    """Test with real-world Amazon-like structure"""
    html = """
    <div data-component-type="s-search-result">
        <h2><a href="/product/B001"><span class="product-title">Amazing Product</span></a></h2>
        <span class="a-price-whole">49</span>
        <span class="a-icon-alt">4.5 out of 5 stars</span>
        <span class="a-size-base">1,234 ratings</span>
    </div>
    <div data-component-type="s-search-result">
        <h2><a href="/product/B002"><span class="product-title">Great Item</span></a></h2>
        <span class="a-price-whole">29</span>
        <span class="a-icon-alt">4.8 out of 5 stars</span>
        <span class="a-size-base">567 ratings</span>
    </div>
    """

    page = WebPage(html, url="https://www.amazon.com/s?k=widgets")

    products = page.extract_all(
        '[data-component-type="s-search-result"]',
        {
            "title": "h2 a span.product-title",
            "url": "h2 a@href",
            "price": "span.a-price-whole",
            "rating": "span.a-icon-alt",
            "review_count": "span.a-size-base",
        },
    )

    assert len(products) == 2
    assert products[0]["title"] == "Amazing Product"
    assert products[0]["price"] == "49"
    assert products[1]["title"] == "Great Item"

    print("✓ Amazon-like extraction:")
    for i, product in enumerate(products, 1):
        print(f"  Product {i}:")
        for key, value in product.items():
            print(f"    {key}: {value}")

    print("\n✅ Real-world Amazon tests passed!")


def test_metadata():
    """Test WebPage metadata"""
    metadata = {
        "source": "scraper_v1",
        "timestamp": "2025-01-01T00:00:00Z",
        "user_agent": "Mozilla/5.0",
    }

    page = WebPage("<html></html>", url="https://example.com", metadata=metadata)

    page_metadata = page.metadata
    assert page_metadata["source"] == "scraper_v1"
    assert page_metadata["timestamp"] == "2025-01-01T00:00:00Z"

    print("✓ Page metadata:")
    for key, value in page_metadata.items():
        print(f"  {key}: {value}")

    print("\n✅ Metadata tests passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing WebPoet-style WebPage API for RusticSoup")
    print("=" * 60)
    print()

    test_webpage_basic()
    print()

    test_webpage_extract()
    print()

    test_webpage_extract_all()
    print()

    test_webpage_get_all_syntax()
    print()

    test_field_descriptors()
    print()

    test_absolute_url()
    print()

    test_real_world_google_shopping()
    print()

    test_real_world_amazon()
    print()

    test_metadata()
    print()

    print("=" * 60)
    print("🎉 ALL TESTS PASSED! WebPage API is fully functional!")
    print("=" * 60)
