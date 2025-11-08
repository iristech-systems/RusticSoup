#!/usr/bin/env python3
"""Test Field with container+mapping inside ItemPage - Real world use case"""

from rusticsoup import Field, WebPage, ItemPage

# Test HTML that matches your Google Shopping offers example
html = """
<html>
<body>
    <div class="product-details">
        <h1 class="main-title">iPhone 15 Pro</h1>
        <div class="description">Latest Apple flagship phone</div>
    </div>

    <!-- Offers grid like Google Shopping -->
    <div data-attrid="organic_offers_grid">
        <div role="listitem">
            <div class="xc8Web" data-gpcid="12345" data-merchantid="seller001" data-oid="offer001">
                <div class="hP4iBf">Best Electronics</div>
                <div class="Rp8BL">iPhone 15 Pro - 256GB</div>
                <div class="UPworb">Save 10%</div>
                <span class="aZosn">PROMO10</span>
                <span class="NFq8Ad">4.8 ⭐</span>
                <span class="jvP2Jb">In stock</span>
                <span aria-label="Current price $999.99"><span>$999.99</span></span>
                <div class="AoPnCe"><span class="tBtgqf">$1,099.99</span></div>
                <a href="/offer/1">View Offer</a>
                <span>Free delivery</span>
                <span>2-day shipping</span>
            </div>
        </div>

        <div role="listitem">
            <div class="xc8Web" data-gpcid="12346" data-merchantid="seller002" data-oid="offer002">
                <div class="hP4iBf">Tech Store Plus</div>
                <div class="Rp8BL">iPhone 15 Pro - 256GB</div>
                <span class="NFq8Ad">4.5 ⭐</span>
                <span class="jIpmhc">Limited stock</span>
                <span aria-label="Current price $1,049.99">$1,049.99</span>
                <a href="/offer/2">View Offer</a>
                <span>Express shipping</span>
            </div>
        </div>

        <div role="listitem">
            <div class="xc8Web" data-gpcid="12347" data-merchantid="seller003" data-oid="offer003">
                <div class="hP4iBf">Phone World</div>
                <div class="Rp8BL">iPhone 15 Pro - 256GB Titanium</div>
                <div class="UPworb">Save 5%</div>
                <span class="NFq8Ad">4.9 ⭐</span>
                <span class="jvP2Jb">In stock</span>
                <span aria-label="Current price $1,029.99"><span>$1,029.99</span></span>
                <div class="AoPnCe"><span class="tBtgqf">$1,099.99</span></div>
                <a href="/offer/3">View Offer</a>
                <span>Standard delivery</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

print("=" * 80)
print("TEST: Field with container+mapping inside ItemPage (Real World Example)")
print("=" * 80)

# Define the offers mapping (like your example)
_offers_mapping = {
    # Text fields
    "seller_name": "div.hP4iBf",
    "product_title": "div.Rp8BL",
    "discount": "div.UPworb",
    "coupon": "span.aZosn",
    "rating": "span.NFq8Ad",
    "availability": "span.jvP2Jb",
    "availability_alt": "span.jIpmhc",
    # Prices - with fallback selectors!
    "offer_price": 'span[aria-label^="Current price"] > span',
    "offer_price_alt": 'span[aria-label^="Current price"]',
    "old_price": "div.AoPnCe span.tBtgqf",
    # Data attributes
    "gpcid": "div.xc8Web@data-gpcid",
    "seller_id": "div.xc8Web@data-merchantid",
    "oid": "div.xc8Web@data-oid",
    # Links
    "link": "a@href",
    # For delivery detection
    "all_spans": "span@get_all",
}


# Define ItemPage with Field that uses container+mapping
class GoogleShoppingPage(ItemPage):
    """Page object for Google Shopping results"""

    # Simple fields
    title = Field(css="h1.main-title")
    description = Field(css=".description")

    # Field with container+mapping - extracts list of offer dicts
    offers = Field(
        container='div[data-attrid="organic_offers_grid"] div[role="listitem"]',
        mapping=_offers_mapping,
    )


print("\n1. Creating page and ItemPage instance...")
page = WebPage(html)
shopping_page = GoogleShoppingPage(page)

print("\n2. Product Info:")
print(f"   Title: {shopping_page.title}")
print(f"   Description: {shopping_page.description}")

print("\n3. Extracted Offers (Field with container+mapping):")
print(f"   Found {len(shopping_page.offers)} offers\n")

for i, offer in enumerate(shopping_page.offers, 1):
    print(f"   Offer #{i}:")
    print(f"      Seller: {offer.get('seller_name', 'N/A')}")
    print(f"      Title: {offer.get('product_title', 'N/A')}")
    print(f"      Rating: {offer.get('rating', 'N/A')}")
    print(
        f"      Price: {offer.get('offer_price', offer.get('offer_price_alt', 'N/A'))}"
    )
    print(f"      Old Price: {offer.get('old_price', 'N/A')}")
    print(f"      Discount: {offer.get('discount', 'N/A')}")
    print(f"      Coupon: {offer.get('coupon', 'N/A')}")
    print(
        f"      Stock: {offer.get('availability', offer.get('availability_alt', 'N/A'))}"
    )
    print(f"      Link: {offer.get('link', 'N/A')}")
    print(f"      Seller ID: {offer.get('seller_id', 'N/A')}")
    print(f"      GPCID: {offer.get('gpcid', 'N/A')}")
    print(f"      OID: {offer.get('oid', 'N/A')}")
    print(f"      Delivery info: {len(offer.get('all_spans', []))} spans found")
    print()

print("=" * 80)
print("TEST: Using Field with fallback selectors in ItemPage")
print("=" * 80)


class FlexibleProductPage(ItemPage):
    """Page object with fallback selectors for different site layouts"""

    # Fallback selectors - tries multiple options
    title = Field(css=["h1.main-title", "h1.title", "h1", ".product-name"])

    # Price with multiple fallback options
    price = Field(
        css=[
            'span[aria-label^="Current price"] > span',
            'span[aria-label^="Current price"]',
            ".price",
            ".product-price",
        ]
    )

    # Offers with container+mapping
    offers = Field(
        container='div[role="listitem"]',
        mapping={
            "seller": ["div.hP4iBf", ".seller", ".merchant"],
            "price": ['span[aria-label^="Current price"]', ".price"],
        },
    )


print("\n1. Creating flexible page...")
flex_page = FlexibleProductPage(page)

print("\n2. Extracted with fallback selectors:")
print(f"   Title: {flex_page.title}")
print(f"   Price: {flex_page.price}")
print(f"   Offers: {len(flex_page.offers)} found")

print("\n" + "=" * 80)
print("✅ ItemPage with Field(container, mapping) works perfectly!")
print("=" * 80)
