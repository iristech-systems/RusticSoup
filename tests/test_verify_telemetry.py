from rusticsoup import WebPage, ItemPage, Field, init_telemetry, shutdown_telemetry

def test_telemetry_integration():
    print("Initializing telemetry with console output...")
    # Initialize with default/no-op to prevent errors if no collector
    # In a real test we might point to a mock collector, but here we testing integration stability
    init_telemetry(endpoint=None, console=True) 
    
    html = """
    <html>
        <body>
            <h1>Test Title</h1>
            <div class="price">$10.00</div>
        </body>
    </html>
    """
    
    class ProductPage(ItemPage):
        title = Field(css="h1")
        price = Field(css=".price")
        
    print("Parsing page...")
    page = WebPage(html)
    
    print("Extracting item (should trigger spans)...")
    product = ProductPage(page)
    
    print(f"Extracted: {product.title}, {product.price}")
    
    assert product.title == "Test Title"
    assert product.price == "$10.00"
    
    print("Shutting down telemetry...")
    shutdown_telemetry()
    print("Success!")

if __name__ == "__main__":
    test_telemetry_integration()
