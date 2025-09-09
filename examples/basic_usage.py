#!/usr/bin/env python3
"""
RusticSoup Basic Usage Examples
"""

import rusticsoup

def example_basic_extraction():
    """Basic HTML data extraction"""
    print("🔧 Basic Extraction Example")
    print("=" * 50)
    
    html = """
    <div class="product">
        <h2>Amazing Product</h2>
        <span class="price">$29.99</span>
        <a href="/buy" class="buy-btn">Buy Now</a>
        <img src="/image.jpg" alt="product">
    </div>
    <div class="product">
        <h2>Another Product</h2>
        <span class="price">$49.99</span>
        <a href="/buy2" class="buy-btn">Buy Now</a>
        <img src="/image2.jpg" alt="product">
    </div>
    """
    
    # Universal extraction - works with any HTML structure
    field_mappings = {
        "title": "h2",              # Text content
        "price": "span.price",      # Text content
        "link": "a.buy-btn@href",   # Attribute extraction with @
        "image": "img@src"          # Any attribute: @src, @href, @alt, etc.
    }
    
    products = rusticsoup.extract_data(html, "div.product", field_mappings)
    
    print(f"✅ Extracted {len(products)} products:")
    for i, product in enumerate(products, 1):
        print(f"  Product {i}: {product}")

def example_nested_extraction():
    """Nested and list extraction example"""
    print("\n📦 Nested and List Extraction Example")
    print("=" * 50)
    
    html = """
    <div class="comment">
        <div class="author">
            <span class="author-name">Alice</span>
            <a class="author-link" href="/users/alice">Profile</a>
        </div>
        <div class="comment-body">
            <p>This is a great library!</p>
            <ul>
                <li>Easy to use</li>
                <li>Fast</li>
            </ul>
        </div>
    </div>
    """
    
    field_mappings = {
        "author": {
            "name": ".author-name",
            "link": ".author-link@href"
        },
        "comment": ".comment-body p",
        "tags": "li@get_all"
    }
    
    # extract_data returns a list of items, one for each matching container
    data = rusticsoup.extract_data(html, ".comment", field_mappings)
    
    print(f"✅ Extracted {len(data)} items:")
    for item in data:
        print(f"  - {item}")

def example_table_extraction():
    """Table data extraction"""
    print("\n📊 Table Extraction Example")
    print("=" * 50)
    
    html = """
    <table class="data-table">
        <tr><th>Name</th><th>Age</th><th>City</th></tr>
        <tr><td>John</td><td>25</td><td>New York</td></tr>
        <tr><td>Jane</td><td>30</td><td>San Francisco</td></tr>
        <tr><td>Bob</td><td>35</td><td>Chicago</td></tr>
    </table>
    """
    
    table_data = rusticsoup.extract_table_data(html, 'table.data-table')
    
    print(f"✅ Extracted {len(table_data)} rows:")
    for row_idx, row in enumerate(table_data):
        print(f"  Row {row_idx}: {row}")

def example_low_level_parsing():
    """Low-level parsing example"""
    print("\n🔧 Low-Level Parsing Example")
    print("=" * 50)
    
    html = """
    <div class="container">
        <h1>Page Title</h1>
        <p>Some content</p>
        <a href="/link" id="main-link">Click here</a>
    </div>
    """
    
    # Low-level parsing for manual DOM traversal
    scraper = rusticsoup.parse_html(html)
    
    # Select elements
    title = scraper.select('h1')[0].text() if scraper.select('h1') else 'No title'
    links = scraper.select('a')
    
    print(f"Title: {title}")
    print(f"Found {len(links)} links:")
    for link in links:
        href = link.attr('href')
        text = link.text()
        print(f"  - {text}: {href}")

if __name__ == "__main__":
    print("🦀 RusticSoup Usage Examples")
    print("=" * 80)
    print("Lightning-fast HTML parser and data extractor built in Rust")
    print("The BeautifulSoup killer with browser-grade parsing performance\n")
    
    # Run all examples
    example_basic_extraction()
    example_nested_extraction()
    example_table_extraction()
    example_low_level_parsing()
    
    print(f"\n🎯 Key Takeaways:")
    print("✅ Universal - works with any HTML structure")
    print("✅ Fast - 2-10x faster than BeautifulSoup")
    print("✅ Simple - one function call extracts structured data")
    print("✅ Attributes - @href, @src syntax for attribute extraction")
    print("✅ Nested data - supports nested dictionaries for complex extraction")
    print("✅ List extraction - use @get_all to extract all matching elements")
    print("✅ No manual loops - RusticSoup handles everything")