"""
Test ItemPage with extract_all pattern
"""

from rusticsoup import WebPage, Field, ItemPage


def test_extract_all_with_itempage():
    """Test extract_all with ItemPage class"""
    html = """
    <html>
        <body>
            <div class="review">
                <span class="author">Alice</span>
                <span class="rating">5</span>
                <p class="text">Great product!</p>
            </div>
            <div class="review">
                <span class="author">Bob</span>
                <span class="rating">4</span>
                <p class="text">Good quality</p>
            </div>
            <div class="review">
                <span class="author">Charlie</span>
                <span class="rating">3</span>
                <p class="text">It's okay</p>
            </div>
        </body>
    </html>
    """

    class Review(ItemPage):
        author = Field(css=".author")
        rating = Field(css=".rating")
        text = Field(css=".text")

    page = WebPage(html)
    reviews = page.extract_all(".review", Review)

    assert len(reviews) == 3

    assert reviews[0].author == "Alice"
    assert reviews[0].rating == "5"
    assert reviews[0].text == "Great product!"

    assert reviews[1].author == "Bob"
    assert reviews[1].rating == "4"
    assert reviews[1].text == "Good quality"

    assert reviews[2].author == "Charlie"
    assert reviews[2].rating == "3"
    assert reviews[2].text == "It's okay"


def test_extract_all_with_itempage_transforms():
    """Test extract_all with ItemPage class and field transforms"""
    html = """
    <html>
        <body>
            <div class="product">
                <h3 class="title">Laptop</h3>
                <span class="price">$999.99</span>
                <a href="/laptops/1">View</a>
            </div>
            <div class="product">
                <h3 class="title">Mouse</h3>
                <span class="price">$29.99</span>
                <a href="/mice/2">View</a>
            </div>
        </body>
    </html>
    """

    def parse_price(s):
        return float(s.replace("$", "").replace(",", ""))

    class Product(ItemPage):
        title = Field(css=".title", transform=str.upper)
        price = Field(css=".price", transform=parse_price)
        link = Field(css="a", attr="href")

    page = WebPage(html)
    products = page.extract_all(".product", Product)

    assert len(products) == 2

    assert products[0].title == "LAPTOP"
    assert products[0].price == 999.99
    assert products[0].link == "/laptops/1"

    assert products[1].title == "MOUSE"
    assert products[1].price == 29.99
    assert products[1].link == "/mice/2"


def test_extract_all_with_itempage_fallback_selectors():
    """Test extract_all with ItemPage class using fallback selectors"""
    html = """
    <html>
        <body>
            <div class="item">
                <span class="price-new">$50</span>
                <span class="availability">In Stock</span>
            </div>
            <div class="item">
                <span class="price-old">$60</span>
                <span class="stock">Available</span>
            </div>
        </body>
    </html>
    """

    class Item(ItemPage):
        price = Field(css=[".price-new", ".price-old"])
        availability = Field(css=[".availability", ".stock"])

    page = WebPage(html)
    items = page.extract_all(".item", Item)

    assert len(items) == 2
    assert items[0].price == "$50"
    assert items[0].availability == "In Stock"
    assert items[1].price == "$60"
    assert items[1].availability == "Available"


def test_field_mapping_with_field_objects():
    """Test Field with container+mapping using Field objects instead of strings"""
    html = """
    <html>
        <body>
            <div class="offer">
                <h3 class="title">Special Deal</h3>
                <span class="price">$19.99</span>
                <span class="discount">20% off</span>
            </div>
            <div class="offer">
                <h3 class="title">Hot Sale</h3>
                <span class="price">$29.99</span>
                <span class="discount">15% off</span>
            </div>
        </body>
    </html>
    """

    def parse_price(s):
        return float(s.replace("$", ""))

    # Use Field objects in mapping for per-field transforms
    offers_field = Field(
        container=".offer",
        mapping={
            "title": Field(css=".title", transform=str.upper),
            "price": Field(css=".price", transform=parse_price),
            "discount": Field(css=".discount"),
        },
    )

    page = WebPage(html)
    offers = offers_field.extract(page)

    assert len(offers) == 2
    assert offers[0]["title"] == "SPECIAL DEAL"
    assert offers[0]["price"] == 19.99
    assert offers[0]["discount"] == "20% off"

    assert offers[1]["title"] == "HOT SALE"
    assert offers[1]["price"] == 29.99
    assert offers[1]["discount"] == "15% off"


def test_extract_all_backward_compatibility():
    """Ensure dict-based extraction still works"""
    html = """
    <html>
        <body>
            <div class="item">
                <span class="name">Item 1</span>
                <span class="value">100</span>
            </div>
            <div class="item">
                <span class="name">Item 2</span>
                <span class="value">200</span>
            </div>
        </body>
    </html>
    """

    page = WebPage(html)
    items = page.extract_all(".item", {"name": ".name", "value": ".value"})

    assert len(items) == 2
    assert items[0]["name"] == "Item 1"
    assert items[0]["value"] == "100"
    assert items[1]["name"] == "Item 2"
    assert items[1]["value"] == "200"


if __name__ == "__main__":
    print("Testing extract_all with ItemPage...")
    test_extract_all_with_itempage()
    print("✓ extract_all with ItemPage works")

    print("\nTesting extract_all with ItemPage transforms...")
    test_extract_all_with_itempage_transforms()
    print("✓ extract_all with ItemPage transforms works")

    print("\nTesting extract_all with ItemPage fallback selectors...")
    test_extract_all_with_itempage_fallback_selectors()
    print("✓ extract_all with ItemPage fallback selectors works")

    print("\nTesting Field mapping with Field objects...")
    test_field_mapping_with_field_objects()
    print("✓ Field mapping with Field objects works")

    print("\nTesting extract_all backward compatibility...")
    test_extract_all_backward_compatibility()
    print("✓ extract_all backward compatibility works")

    print("\n" + "=" * 50)
    print("All ItemPage extract_all tests passed! ✓")
    print("=" * 50)
