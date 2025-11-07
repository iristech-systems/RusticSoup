"""
Test and demonstrate Field usage in RusticSoup

The Field class provides declarative field descriptors for reusable extraction patterns.
"""

from rusticsoup import WebPage, Field


def test_field_basics():
    """Test basic Field usage"""
    html = """
    <article>
        <h1>Understanding Rust</h1>
        <span class="author">Jane Smith</span>
        <div class="content">Rust is a systems programming language...</div>
        <a href="/articles/rust-101">Read more</a>
        <img src="/images/rust-logo.png" alt="Rust Logo">
    </article>
    """

    page = WebPage(html, url="https://blog.example.com/rust-101")

    # Define reusable field extractors
    title_field = Field(css="h1")
    author_field = Field(css="span.author")
    content_field = Field(css="div.content")
    link_field = Field(css="a", attr="href")
    image_field = Field(css="img", attr="src")
    image_alt_field = Field(css="img", attr="alt")

    # Extract using fields
    print("=" * 60)
    print("Basic Field Extraction")
    print("=" * 60)

    title = title_field.extract(page)
    author = author_field.extract(page)
    content = content_field.extract(page)
    link = link_field.extract(page)
    image = image_field.extract(page)
    image_alt = image_alt_field.extract(page)

    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Content: {content[:50]}...")
    print(f"Link: {link}")
    print(f"Image: {image}")
    print(f"Image Alt: {image_alt}")

    assert title == "Understanding Rust"
    assert author == "Jane Smith"
    assert link == "/articles/rust-101"

    print("\n✅ Basic field extraction passed!")


def test_field_get_all():
    """Test Field with get_all=True"""
    html = """
    <article>
        <h2>Web Scraping Guide</h2>
        <p>First paragraph about web scraping.</p>
        <p>Second paragraph with more details.</p>
        <p>Third paragraph with examples.</p>
        <span class="tag">Python</span>
        <span class="tag">Web Scraping</span>
        <span class="tag">Automation</span>
        <a href="/tag/python">Python</a>
        <a href="/tag/scraping">Scraping</a>
        <a href="/tag/automation">Automation</a>
    </article>
    """

    page = WebPage(html)

    # Fields that extract all matching elements
    paragraphs_field = Field(css="p", get_all=True)
    tags_field = Field(css="span.tag", get_all=True)
    tag_links_field = Field(css="a", attr="href", get_all=True)

    print("\n" + "=" * 60)
    print("Field with get_all=True")
    print("=" * 60)

    paragraphs = paragraphs_field.extract(page)
    tags = tags_field.extract(page)
    tag_links = tag_links_field.extract(page)

    print(f"Paragraphs ({len(paragraphs)} items):")
    for i, p in enumerate(paragraphs, 1):
        print(f"  {i}. {p[:40]}...")

    print(f"\nTags ({len(tags)} items): {tags}")
    print(f"Tag Links ({len(tag_links)} items): {tag_links}")

    assert len(paragraphs) == 3
    assert len(tags) == 3
    assert len(tag_links) == 3
    assert "Python" in tags

    print("\n✅ get_all field extraction passed!")


def test_field_reusability():
    """Test Field reusability across multiple pages"""
    # Define fields once, use on multiple pages
    title_field = Field(css="h1.title")
    author_field = Field(css="span.author")
    date_field = Field(css="time", attr="datetime")
    tags_field = Field(css=".tag", get_all=True)

    print("\n" + "=" * 60)
    print("Field Reusability")
    print("=" * 60)

    # Page 1
    html1 = """
    <article>
        <h1 class="title">First Article</h1>
        <span class="author">Alice</span>
        <time datetime="2025-01-01">Jan 1, 2025</time>
        <span class="tag">Tech</span>
        <span class="tag">AI</span>
    </article>
    """

    page1 = WebPage(html1)
    article1 = {
        "title": title_field.extract(page1),
        "author": author_field.extract(page1),
        "date": date_field.extract(page1),
        "tags": tags_field.extract(page1),
    }

    # Page 2
    html2 = """
    <article>
        <h1 class="title">Second Article</h1>
        <span class="author">Bob</span>
        <time datetime="2025-01-02">Jan 2, 2025</time>
        <span class="tag">Python</span>
        <span class="tag">Web</span>
    </article>
    """

    page2 = WebPage(html2)
    article2 = {
        "title": title_field.extract(page2),
        "author": author_field.extract(page2),
        "date": date_field.extract(page2),
        "tags": tags_field.extract(page2),
    }

    print("Article 1:")
    for key, value in article1.items():
        print(f"  {key}: {value}")

    print("\nArticle 2:")
    for key, value in article2.items():
        print(f"  {key}: {value}")

    assert article1["title"] == "First Article"
    assert article2["title"] == "Second Article"
    assert len(article1["tags"]) == 2
    assert len(article2["tags"]) == 2

    print("\n✅ Field reusability passed!")


def test_field_vs_direct_extraction():
    """Compare Field usage vs direct WebPage methods"""
    html = """
    <div class="product">
        <h2>Awesome Product</h2>
        <span class="price">$99.99</span>
        <a href="/products/123">View Details</a>
        <img src="/images/product.jpg">
    </div>
    """

    page = WebPage(html)

    print("\n" + "=" * 60)
    print("Field vs Direct Extraction Comparison")
    print("=" * 60)

    # Method 1: Direct WebPage methods
    print("\nMethod 1: Direct WebPage methods")
    product_direct = {
        "title": page.text("h2"),
        "price": page.text("span.price"),
        "url": page.attr("a", "href"),
        "image": page.attr("img", "src"),
    }
    print(f"  {product_direct}")

    # Method 2: Using Field objects (reusable)
    print("\nMethod 2: Using Field objects (reusable)")
    title_field = Field(css="h2")
    price_field = Field(css="span.price")
    url_field = Field(css="a", attr="href")
    image_field = Field(css="img", attr="src")

    product_fields = {
        "title": title_field.extract(page),
        "price": price_field.extract(page),
        "url": url_field.extract(page),
        "image": image_field.extract(page),
    }
    print(f"  {product_fields}")

    # Both methods produce same results
    assert product_direct == product_fields

    print("\n✅ Both methods produce identical results!")
    print("\n💡 Use Fields when:")
    print("   - You need to reuse extraction patterns")
    print("   - Building a library of extractors")
    print("   - Want declarative field definitions")
    print("\n💡 Use WebPage methods when:")
    print("   - Quick one-off extractions")
    print("   - Simple scripts")
    print("   - Prefer functional style")


def test_field_field_configuration():
    """Test Field with different configurations"""
    html = """
    <article>
        <h1>Title</h1>
        <span class="optional">Optional Text</span>
        <span class="missing">This element doesn't exist</span>
        <div class="items">
            <span>Item 1</span>
            <span>Item 2</span>
            <span>Item 3</span>
        </div>
    </article>
    """

    page = WebPage(html)

    print("\n" + "=" * 60)
    print("Field Configuration Options")
    print("=" * 60)

    # Text extraction
    title_field = Field(css="h1")
    title = title_field.extract(page)
    print(f"Text extraction: {title}")

    # Attribute extraction
    # Note: No element with this attribute in this example
    link_field = Field(css="a", attr="href")
    link = link_field.extract(page)
    print(f"Attribute extraction (missing): {repr(link)}")

    # Multiple items
    items_field = Field(css="div.items span", get_all=True)
    items = items_field.extract(page)
    print(f"Multiple items: {items}")

    print("\n✅ Field configuration test passed!")


if __name__ == "__main__":
    test_field_basics()
    test_field_get_all()
    test_field_reusability()
    test_field_vs_direct_extraction()
    test_field_field_configuration()

    print("\n" + "=" * 60)
    print("🎉 All Field tests passed!")
    print("=" * 60)
    print("\n📚 Field Usage Summary:")
    print("  • Field objects define reusable extraction patterns")
    print("  • Use field.extract(page) to extract from a WebPage")
    print("  • Set get_all=True to extract from all matching elements")
    print("  • Set attr='name' to extract attributes instead of text")
    print("  • Fields are perfect for building extraction libraries")
