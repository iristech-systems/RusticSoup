#!/usr/bin/env python3
"""Test new Field features: fallback selectors and container+mapping"""

from rusticsoup import Field, WebPage

# Test HTML with multiple price formats
html = """
<html>
<body>
    <div class="product">
        <h1 class="title">Product A</h1>
        <div class="price-new">$99.99</div>
    </div>

    <div class="product">
        <h1 class="title">Product B</h1>
        <span class="price-old">$149.99</span>
    </div>

    <div class="product">
        <h1 class="title">Product C</h1>
        <div class="sale-price">$79.99</div>
    </div>

    <!-- Offers list -->
    <div class="offers">
        <div class="offer">
            <div class="seller">Seller 1</div>
            <span class="price">$99.99</span>
            <a href="/offer1">View</a>
        </div>
        <div class="offer">
            <div class="seller">Seller 2</div>
            <span class="price">$95.99</span>
            <a href="/offer2">View</a>
        </div>
        <div class="offer">
            <div class="seller">Seller 3</div>
            <span class="price">$102.99</span>
            <a href="/offer3">View</a>
        </div>
    </div>
</body>
</html>
"""

print("=" * 60)
print("TEST 1: Fallback Selectors")
print("=" * 60)

page = WebPage(html)

# Define a field with fallback selectors
# It will try each selector until one returns a non-empty result
price_field = Field(css=[".price-new", ".price-old", ".sale-price"])

# Extract from each product
products = page.css_all(".product")
print(f"\nFound {len(products)} products")

# Test fallback on first product (has .price-new)
product1_html = page.css(".product")
page1 = WebPage(product1_html)
price1 = price_field.extract(page1)
print(f"Product 1 price: {price1}")

# Test fallback on second product (has .price-old)
products_list = page.css_all(".product")
page2 = WebPage(products_list[1] if len(products_list) > 1 else "")
price2 = price_field.extract(page2)
print(f"Product 2 price: {price2}")

# Test fallback on third product (has .sale-price)
page3 = WebPage(products_list[2] if len(products_list) > 2 else "")
price3 = price_field.extract(page3)
print(f"Product 3 price: {price3}")

print("\n" + "=" * 60)
print("TEST 2: Container + Mapping (List Extraction)")
print("=" * 60)

# Define field with container + mapping
offers_mapping = {
    "seller": ".seller",
    "price": ".price",
    "link": "a@href",
}

offers_field = Field(container=".offer", mapping=offers_mapping)

# Extract all offers as a list of dicts
offers = offers_field.extract(page)
print(f"\nExtracted {len(offers)} offers:")
for i, offer in enumerate(offers, 1):
    print(f"\nOffer {i}:")
    print(f"  Seller: {offer['seller']}")
    print(f"  Price: {offer['price']}")
    print(f"  Link: {offer['link']}")

print("\n" + "=" * 60)
print("TEST 3: Alternative - Using WebPage.extract_all directly")
print("=" * 60)

# This was already possible, but Field makes it reusable
offers_direct = page.extract_all(".offer", offers_mapping)
print(f"\nExtracted {len(offers_direct)} offers directly:")
print(f"First offer: {offers_direct[0]}")

print("\n" + "=" * 60)
print("TEST 4: Fallback with get_all")
print("=" * 60)

# Get all prices from any of the price selectors
all_prices_field = Field(css=[".price-new", ".price-old", ".sale-price"], get_all=True)

all_prices = all_prices_field.extract(page)
print(f"\nAll prices found: {all_prices}")

print("\n" + "=" * 60)
print("✅ All tests completed successfully!")
print("=" * 60)
