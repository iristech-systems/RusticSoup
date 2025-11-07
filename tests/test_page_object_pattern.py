"""
Test PageObject Pattern - Auto-extraction from Field definitions

This demonstrates three ways to use the PageObject pattern with RusticSoup:
1. ItemPage base class (Recommended)
2. @page_object decorator
3. Manual extraction with Fields
"""

from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage, page_object


def test_item_page_basic():
    """Test ItemPage with auto-extraction"""
    html = """
    <article>
        <h1>Understanding Rust and Python</h1>
        <span class="author">Jane Smith</span>
        <time datetime="2025-01-07">January 7, 2025</time>
        <div class="content">
            <p>First paragraph of the article.</p>
            <p>Second paragraph with more details.</p>
            <p>Third paragraph concluding the article.</p>
        </div>
        <span class="tag">Rust</span>
        <span class="tag">Python</span>
        <span class="tag">Programming</span>
    </article>
    """

    # Define page object class
    class Article(ItemPage):
        title = Field(css="h1")
        author = Field(css=".author")
        date = Field(css="time", attr="datetime")
        paragraphs = Field(css=".content p", get_all=True)
        tags = Field(css=".tag", get_all=True)

    print("=" * 60)
    print("Test 1: ItemPage with Auto-Extraction")
    print("=" * 60)

    # Create page and auto-extract
    page = WebPage(html, url="https://blog.example.com/article")
    article = Article(page)

    # Access extracted fields directly
    print(f"\nTitle: {article.title}")
    print(f"Author: {article.author}")
    print(f"Date: {article.date}")
    print(f"Paragraphs: {len(article.paragraphs)} paragraphs")
    print(f"Tags: {article.tags}")

    # Assertions
    assert article.title == "Understanding Rust and Python"
    assert article.author == "Jane Smith"
    assert article.date == "2025-01-07"
    assert len(article.paragraphs) == 3
    assert len(article.tags) == 3
    assert "Rust" in article.tags

    # Convert to dict
    article_dict = article.to_dict()
    print(f"\nAs dict: {list(article_dict.keys())}")
    assert "title" in article_dict
    assert "tags" in article_dict

    print("\n✅ ItemPage auto-extraction works!")


def test_page_object_decorator():
    """Test @page_object decorator"""
    html = """
    <div class="product">
        <h2 class="title">Wireless Mouse</h2>
        <span class="price">$24.99</span>
        <span class="original-price">$34.99</span>
        <div class="rating">4.5 stars</div>
        <span class="reviews">1,234 reviews</span>
        <img src="/images/mouse.jpg" alt="Mouse">
        <img src="/images/mouse-angle.jpg" alt="Mouse Angle">
        <img src="/images/mouse-top.jpg" alt="Mouse Top">
    </div>
    """

    # Use decorator
    @page_object
    class Product:
        title = Field(css="h2.title")
        price = Field(css=".price")
        original_price = Field(css=".original-price")
        rating = Field(css=".rating")
        reviews = Field(css=".reviews")
        main_image = Field(css="img", attr="src")
        all_images = Field(css="img", attr="src", get_all=True)

    print("\n" + "=" * 60)
    print("Test 2: @page_object Decorator")
    print("=" * 60)

    # Auto-extract
    page = WebPage(html, url="https://shop.example.com/mouse")
    product = Product(page)

    # Access fields
    print(f"\nTitle: {product.title}")
    print(f"Price: {product.price}")
    print(f"Original Price: {product.original_price}")
    print(f"Rating: {product.rating}")
    print(f"Reviews: {product.reviews}")
    print(f"Images: {len(product.all_images)} images")

    # Assertions
    assert product.title == "Wireless Mouse"
    assert product.price == "$24.99"
    assert product.original_price == "$34.99"
    assert len(product.all_images) == 3
    assert "/images/mouse.jpg" in product.all_images

    # Convert to dict
    product_dict = product.to_dict()
    print(f"\nAs dict: {list(product_dict.keys())}")

    print("\n✅ @page_object decorator works!")


def test_reusable_page_objects():
    """Test reusing page object classes across multiple pages"""

    # Define once
    class BlogPost(ItemPage):
        title = Field(css="h1.post-title")
        author = Field(css=".author-name")
        date = Field(css="time", attr="datetime")
        tags = Field(css=".tag", get_all=True)

    print("\n" + "=" * 60)
    print("Test 3: Reusable Page Objects")
    print("=" * 60)

    # HTML for post 1
    html1 = """
    <article>
        <h1 class="post-title">First Post</h1>
        <span class="author-name">Alice</span>
        <time datetime="2025-01-01">Jan 1</time>
        <span class="tag">Tech</span>
        <span class="tag">AI</span>
    </article>
    """

    # HTML for post 2
    html2 = """
    <article>
        <h1 class="post-title">Second Post</h1>
        <span class="author-name">Bob</span>
        <time datetime="2025-01-02">Jan 2</time>
        <span class="tag">Python</span>
        <span class="tag">Web</span>
    </article>
    """

    # Extract from both
    page1 = WebPage(html1)
    page2 = WebPage(html2)

    post1 = BlogPost(page1)
    post2 = BlogPost(page2)

    print("\nPost 1:")
    print(f"  Title: {post1.title}")
    print(f"  Author: {post1.author}")
    print(f"  Tags: {post1.tags}")

    print("\nPost 2:")
    print(f"  Title: {post2.title}")
    print(f"  Author: {post2.author}")
    print(f"  Tags: {post2.tags}")

    # Assertions
    assert post1.title == "First Post"
    assert post2.title == "Second Post"
    assert post1.author == "Alice"
    assert post2.author == "Bob"

    print("\n✅ Reusable page objects work!")


def test_nested_extraction():
    """Test extracting complex nested data"""
    html = """
    <div class="product-page">
        <div class="product-info">
            <h1 class="name">Amazing Widget</h1>
            <div class="pricing">
                <span class="current-price">$99.99</span>
                <span class="original-price">$149.99</span>
                <span class="discount">33% off</span>
            </div>
            <div class="seller">
                <span class="seller-name">TechCorp</span>
                <span class="seller-rating">4.8/5</span>
            </div>
        </div>
        <div class="specifications">
            <div class="spec">
                <span class="spec-name">Brand</span>
                <span class="spec-value">WidgetPro</span>
            </div>
            <div class="spec">
                <span class="spec-name">Model</span>
                <span class="spec-value">WP-2000</span>
            </div>
        </div>
    </div>
    """

    class ProductPage(ItemPage):
        # Basic info
        name = Field(css="h1.name")

        # Pricing
        current_price = Field(css=".current-price")
        original_price = Field(css=".original-price")
        discount = Field(css=".discount")

        # Seller
        seller_name = Field(css=".seller-name")
        seller_rating = Field(css=".seller-rating")

        # Specs
        spec_names = Field(css=".spec-name", get_all=True)
        spec_values = Field(css=".spec-value", get_all=True)

    print("\n" + "=" * 60)
    print("Test 4: Complex Nested Extraction")
    print("=" * 60)

    page = WebPage(html)
    product = ProductPage(page)

    print(f"\nProduct: {product.name}")
    print(f"Price: {product.current_price} (was {product.original_price})")
    print(f"Discount: {product.discount}")
    print(f"Seller: {product.seller_name} ({product.seller_rating})")
    print("\nSpecifications:")
    for name, value in zip(product.spec_names, product.spec_values):
        print(f"  {name}: {value}")

    # Assertions
    assert product.name == "Amazing Widget"
    assert product.current_price == "$99.99"
    assert product.seller_name == "TechCorp"
    assert len(product.spec_names) == 2

    print("\n✅ Complex nested extraction works!")


def test_real_world_ecommerce():
    """Real-world e-commerce example"""

    class AmazonProduct(ItemPage):
        """Page object for Amazon-like product pages"""

        title = Field(css="#productTitle")
        price = Field(css=".a-price-whole")
        rating = Field(css=".a-icon-alt")
        review_count = Field(css="#acrCustomerReviewText")
        availability = Field(css="#availability span")
        features = Field(css="#feature-bullets li span", get_all=True)
        images = Field(css=".a-dynamic-image", attr="src", get_all=True)

    html = """
    <div class="product">
        <span id="productTitle">Bluetooth Wireless Mouse</span>
        <span class="a-price-whole">29</span>
        <span class="a-icon-alt">4.5 out of 5 stars</span>
        <span id="acrCustomerReviewText">2,547 ratings</span>
        <div id="availability"><span>In Stock</span></div>
        <div id="feature-bullets">
            <ul>
                <li><span>Wireless connectivity</span></li>
                <li><span>Ergonomic design</span></li>
                <li><span>Long battery life</span></li>
            </ul>
        </div>
        <img class="a-dynamic-image" src="/images/mouse1.jpg">
        <img class="a-dynamic-image" src="/images/mouse2.jpg">
    </div>
    """

    print("\n" + "=" * 60)
    print("Test 5: Real-World E-commerce (Amazon-like)")
    print("=" * 60)

    page = WebPage(html)
    product = AmazonProduct(page)

    print(f"\nProduct: {product.title}")
    print(f"Price: ${product.price}")
    print(f"Rating: {product.rating}")
    print(f"Reviews: {product.review_count}")
    print(f"Availability: {product.availability}")
    print("\nFeatures:")
    for i, feature in enumerate(product.features, 1):
        print(f"  {i}. {feature}")
    print(f"\nImages: {len(product.images)} images")

    # Convert to dict for JSON/database
    product_data = product.to_dict()
    print(f"\nExtracted fields: {list(product_data.keys())}")

    assert product.title == "Bluetooth Wireless Mouse"
    assert product.price == "29"
    assert len(product.features) == 3
    assert len(product.images) == 2

    print("\n✅ Real-world e-commerce extraction works!")


def test_comparison_methods():
    """Compare manual vs auto extraction"""
    html = """
    <article>
        <h1>Article Title</h1>
        <span class="author">John Doe</span>
        <div class="content">Content here</div>
    </article>
    """

    print("\n" + "=" * 60)
    print("Test 6: Comparison of Extraction Methods")
    print("=" * 60)

    page = WebPage(html)

    # Method 1: Manual with Fields
    print("\n1. Manual Field Extraction:")
    title_field = Field(css="h1")
    author_field = Field(css=".author")
    title_manual = title_field.extract(page)
    author_manual = author_field.extract(page)
    print(f"   Title: {title_manual}")
    print(f"   Author: {author_manual}")

    # Method 2: Direct WebPage methods
    print("\n2. Direct WebPage Methods:")
    title_direct = page.text("h1")
    author_direct = page.text(".author")
    print(f"   Title: {title_direct}")
    print(f"   Author: {author_direct}")

    # Method 3: Auto-extraction with ItemPage
    print("\n3. Auto-extraction with ItemPage:")

    class Article(ItemPage):
        title = Field(css="h1")
        author = Field(css=".author")
        content = Field(css=".content")

    article = Article(page)
    print(f"   Title: {article.title}")
    print(f"   Author: {article.author}")
    print(f"   Content: {article.content}")

    # All produce same results
    assert title_manual == title_direct == article.title
    assert author_manual == author_direct == article.author

    print("\n✅ All methods produce identical results!")
    print("\n💡 Choose based on your needs:")
    print("   • ItemPage: Best for reusable, structured extraction")
    print("   • Manual Fields: Good for custom extraction logic")
    print("   • Direct methods: Quick one-off extractions")


if __name__ == "__main__":
    test_item_page_basic()
    test_page_object_decorator()
    test_reusable_page_objects()
    test_nested_extraction()
    test_real_world_ecommerce()
    test_comparison_methods()

    print("\n" + "=" * 60)
    print("🎉 All PageObject Pattern Tests Passed!")
    print("=" * 60)
    print("\n📚 Summary:")
    print("  • ItemPage: Inherit and define Fields as class attributes")
    print("  • Auto-extraction: Fields extracted on instantiation")
    print("  • Reusable: Define once, use on many pages")
    print("  • Clean API: Access fields as attributes")
    print("  • to_dict(): Easy conversion to dict/JSON")
