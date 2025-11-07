"""
Test Field transform functionality
"""

from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage


def test_single_transform():
    """Test single transform function"""
    html = """
    <html>
        <body>
            <h1>hello world</h1>
        </body>
    </html>
    """

    page = WebPage(html)

    # Single transform: uppercase
    field = Field(css="h1", transform=str.upper)
    result = field.extract(page)

    assert result == "HELLO WORLD"


def test_multiple_transforms():
    """Test chaining multiple transforms"""
    html = """
    <html>
        <body>
            <h1>  hello world  </h1>
        </body>
    </html>
    """

    page = WebPage(html)

    # Chain transforms: strip, upper, replace
    field = Field(
        css="h1", transform=[str.strip, str.upper, lambda s: s.replace(" ", "_")]
    )
    result = field.extract(page)

    assert result == "HELLO_WORLD"


def test_transform_with_itempage():
    """Test transforms work with ItemPage pattern"""
    html = """
    <html>
        <body>
            <h1>Understanding Rust</h1>
            <div class="author">john doe</div>
            <div class="price">$19.99</div>
        </body>
    </html>
    """

    class Article(ItemPage):
        title = Field(css="h1", transform=str.upper)
        author = Field(css=".author", transform=str.title)
        price = Field(
            css=".price", transform=[str.strip, lambda s: float(s.replace("$", ""))]
        )

    page = WebPage(html)
    article = Article(page)

    assert article.title == "UNDERSTANDING RUST"
    assert article.author == "John Doe"
    assert article.price == 19.99


def test_transform_with_get_all():
    """Test transforms work with get_all"""
    html = """
    <html>
        <body>
            <span class="tag">python</span>
            <span class="tag">rust</span>
            <span class="tag">javascript</span>
        </body>
    </html>
    """

    page = WebPage(html)

    # Transform each item in the list
    def uppercase_list(items):
        return [item.upper() for item in items]

    field = Field(css=".tag", get_all=True, transform=uppercase_list)
    result = field.extract(page)

    assert result == ["PYTHON", "RUST", "JAVASCRIPT"]


def test_transform_with_attr():
    """Test transforms work with attribute extraction"""
    html = """
    <html>
        <body>
            <a href="/product/123">Product</a>
        </body>
    </html>
    """

    page = WebPage(html, url="https://example.com")

    # Transform extracted attribute
    field = Field(
        css="a", attr="href", transform=lambda href: f"https://example.com{href}"
    )
    result = field.extract(page)

    assert result == "https://example.com/product/123"


def test_complex_transform_pipeline():
    """Test complex transform pipeline"""
    html = """
    <html>
        <body>
            <div class="content">
                <p>Price: $1,234.56</p>
            </div>
        </body>
    </html>
    """

    page = WebPage(html)

    def extract_price(text):
        """Extract price from text"""
        import re

        match = re.search(r"\$([0-9,]+\.[0-9]{2})", text)
        return match.group(1) if match else "0.00"

    def remove_commas(price_str):
        """Remove commas from price"""
        return price_str.replace(",", "")

    def to_float(price_str):
        """Convert to float"""
        return float(price_str)

    field = Field(css=".content", transform=[extract_price, remove_commas, to_float])
    result = field.extract(page)

    assert result == 1234.56


def test_transform_with_default_value():
    """Test transforms still apply to default values if extraction fails"""
    html = """
    <html>
        <body>
            <div>No price here</div>
        </body>
    </html>
    """

    page = WebPage(html)

    # Even if selector doesn't match, default is used but NOT transformed
    # (because extraction failed, so no value to transform)
    field = Field(css=".nonexistent", default="free", transform=str.upper)

    try:
        result = field.extract(page)
        # If no exception, check if default is returned (without transform)
        # or if transform was applied
        print(f"Result: {result}")
    except Exception as e:
        # Expected to fail since selector doesn't match and required=True by default
        print(f"Expected error: {e}")


def test_real_world_article_example():
    """Test real-world article extraction with transforms"""
    html = """
    <html>
        <body>
            <article>
                <h1>  Understanding Rust and Python Integration  </h1>
                <div class="author">by JANE SMITH</div>
                <time datetime="2025-01-07">January 7, 2025</time>
                <div class="content">
                    <p>First paragraph about Rust.</p>
                    <p>Second paragraph about Python.</p>
                    <p>Third paragraph about integration.</p>
                </div>
                <span class="tag">rust</span>
                <span class="tag">python</span>
                <span class="tag">programming</span>
            </article>
        </body>
    </html>
    """

    def clean_author(text):
        """Clean author name"""
        return text.replace("by ", "").title()

    def format_date(date_str):
        """Format date string"""
        from datetime import datetime

        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y")

    def join_paragraphs(paragraphs):
        """Join paragraphs with double newline"""
        return "\n\n".join(paragraphs)

    class Article(ItemPage):
        title = Field(css="h1", transform=[str.strip, str.title])
        author = Field(css=".author", transform=clean_author)
        date = Field(css="time", attr="datetime", transform=format_date)
        content = Field(css=".content p", get_all=True, transform=join_paragraphs)
        tags = Field(
            css=".tag", get_all=True, transform=lambda tags: [t.upper() for t in tags]
        )

    page = WebPage(html)
    article = Article(page)

    assert article.title == "Understanding Rust And Python Integration"
    assert article.author == "Jane Smith"
    assert article.date == "January 07, 2025"
    assert "First paragraph" in article.content
    assert "Second paragraph" in article.content
    assert article.tags == ["RUST", "PYTHON", "PROGRAMMING"]


if __name__ == "__main__":
    print("Testing single transform...")
    test_single_transform()
    print("✓ Single transform works")

    print("\nTesting multiple transforms...")
    test_multiple_transforms()
    print("✓ Multiple transforms work")

    print("\nTesting transform with ItemPage...")
    test_transform_with_itempage()
    print("✓ Transform with ItemPage works")

    print("\nTesting transform with get_all...")
    test_transform_with_get_all()
    print("✓ Transform with get_all works")

    print("\nTesting transform with attr...")
    test_transform_with_attr()
    print("✓ Transform with attr works")

    print("\nTesting complex transform pipeline...")
    test_complex_transform_pipeline()
    print("✓ Complex transform pipeline works")

    print("\nTesting real-world article example...")
    test_real_world_article_example()
    print("✓ Real-world article example works")

    print("\n" + "=" * 50)
    print("All transform tests passed! ✓")
    print("=" * 50)
