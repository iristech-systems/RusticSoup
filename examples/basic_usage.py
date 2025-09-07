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

def example_google_shopping():
    """Google Shopping extraction example"""
    print("\n🛍️  Google Shopping Example")
    print("=" * 50)
    
    html = """
    <div id="sh-osd__online-sellers-cont">
        <table>
            <tr data-is-grid-offer="true">
                <td><a class="b5ycib" href="/url?q=https://www.chewy.com/">Chewy.com</a></td>
                <td><span class="g9WBQb">$50.98</span><div class="drzWO">$55.50</div></td>
                <td><a class="UxuaJe" href="/url?q=https://www.chewy.com/">Visit</a></td>
            </tr>
            <tr data-is-grid-offer="true">
                <td><a class="b5ycib" href="/url?q=https://www.petco.com/">Petco.com</a></td>
                <td><span class="g9WBQb">$52.99</span><div class="drzWO">$57.49</div></td>
                <td><a class="UxuaJe" href="/url?q=https://www.petco.com/">Visit</a></td>
            </tr>
        </table>
    </div>
    """
    
    # No Google Shopping specific logic - pure generic extraction
    field_mappings = {
        'seller_name': 'a.b5ycib',           # Text content
        'offer_price': 'span.g9WBQb',        # Text content  
        'total_price': 'div.drzWO',          # Text content
        'link': 'a.UxuaJe@href'              # Attribute extraction
    }
    
    ads = rusticsoup.extract_data(html, 'tr[data-is-grid-offer="true"]', field_mappings)
    
    print(f"✅ Extracted {len(ads)} ads:")
    for i, ad in enumerate(ads, 1):
        print(f"  Ad {i}: {ad}")

def example_bulk_processing():
    """Bulk processing example"""
    print("\n⚡ Bulk Processing Example")
    print("=" * 50)
    
    # Multiple pages of data
    pages = [
        '<div class="item"><h3>Item A</h3><span class="price">$19.99</span></div>',
        '<div class="item"><h3>Item B</h3><span class="price">$29.99</span></div>',
        '<div class="item"><h3>Item C</h3><span class="price">$39.99</span></div>',
    ]
    
    field_mappings = {
        'name': 'h3',
        'price': 'span.price'
    }
    
    # Process all pages in parallel
    all_results = rusticsoup.extract_data_bulk(pages, 'div.item', field_mappings)
    
    print(f"✅ Processed {len(all_results)} pages:")
    for page_idx, page_results in enumerate(all_results):
        print(f"  Page {page_idx + 1}: {page_results}")

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
    example_google_shopping()
    example_bulk_processing()
    example_table_extraction()
    example_low_level_parsing()
    
    print(f"\n🎯 Key Takeaways:")
    print("✅ Universal - works with any HTML structure")
    print("✅ Fast - 2-10x faster than BeautifulSoup")
    print("✅ Simple - one function call extracts structured data")
    print("✅ Attributes - @href, @src syntax for attribute extraction")
    print("✅ Bulk processing - parallel processing of multiple pages")
    print("✅ No manual loops - RusticSoup handles everything")