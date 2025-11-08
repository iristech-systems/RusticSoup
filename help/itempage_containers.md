# ItemPage: Field(container, mapping) Guide

This guide shows how to use `Field(container=..., mapping=...)` inside an ItemPage to extract a list of structured items (dicts). It mirrors `tests/test_itempage_field.py` with a shortened Google Shopping–style example.

## Concept
- `container`: CSS selector that identifies each item block.
- `mapping`: dict that maps output keys to selectors (supports text, attributes via `@`, and fallbacks via lists).
- Result: a list of dictionaries, one per container match.

## Example: Google Shopping–like offers
```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

html = """
<div class="product-details">
  <h1 class="main-title">iPhone 15 Pro</h1>
  <div class="description">Latest Apple flagship phone</div>
</div>
<div data-attrid="organic_offers_grid">
  <div role="listitem">
    <div class="xc8Web" data-gpcid="12345" data-merchantid="seller001" data-oid="offer001">
      <div class="hP4iBf">Best Electronics</div>
      <div class="Rp8BL">iPhone 15 Pro - 256GB</div>
      <span class="NFq8Ad">4.8 ⭐</span>
      <span aria-label="Current price $999.99"><span>$999.99</span></span>
      <a href="/offer/1">View Offer</a>
      <span>Free delivery</span>
    </div>
  </div>
  <div role="listitem">
    <div class="xc8Web" data-gpcid="12346" data-merchantid="seller002" data-oid="offer002">
      <div class="hP4iBf">Tech Store Plus</div>
      <div class="Rp8BL">iPhone 15 Pro - 256GB</div>
      <span class="NFq8Ad">4.5 ⭐</span>
      <span aria-label="Current price $1,049.99">$1,049.99</span>
      <a href="/offer/2">View Offer</a>
    </div>
  </div>
</div>
"""

# Field mapping with attributes, fallbacks, and lists
offers_mapping = {
    "seller_name": "div.hP4iBf",
    "product_title": "div.Rp8BL",
    "rating": "span.NFq8Ad",
    # price: try nested <span> first, then fallback to aria-label element
    "offer_price": [
        'span[aria-label^="Current price"] > span',
        'span[aria-label^="Current price"]',
    ],
    # data-* attributes on the container div
    "gpcid": "div.xc8Web@data-gpcid",
    "seller_id": "div.xc8Web@data-merchantid",
    "oid": "div.xc8Web@data-oid",
    # link
    "link": "a@href",
    # capture all spans to inspect delivery info etc
    "all_spans": "span@get_all",
}

class GoogleShoppingPage(ItemPage):
    title = Field(css="h1.main-title")
    description = Field(css=".description")
    offers = Field(
        container='div[data-attrid="organic_offers_grid"] div[role="listitem"]',
        mapping=offers_mapping,
    )

page = WebPage(html)
shopping = GoogleShoppingPage(page)
print(shopping.title)
print(len(shopping.offers))   # -> 2
print(shopping.offers[0]["seller_name"], shopping.offers[0]["offer_price"])  # Best Electronics $999.99
```

## Mapping fallbacks
You can provide a list of selectors for any mapping value. The first selector that produces a value wins.
```python
fallback_mapping = {
  "seller": [".hP4iBf", ".seller", ".merchant"],
  "price": [
      'span[aria-label^="Current price"] > span',
      'span[aria-label^="Current price"]',
      '.price',
  ],
}
```

## Tips & Best Practices
- Prefer specific selectors (e.g., `[aria-label^="Current price"]`) to avoid noise.
- For attributes, use `@attr` suffix (e.g., `a@href`, `div.xc8Web@data-merchantid`).
- Use `get_all` in mapping to capture lists (e.g., all badges/spans).
- Keep mapping keys stable and descriptive so downstream code stays simple.

## See Also
- Containers & Mappings (overview): ./containers_and_mappings.md
- PageObject Pattern: ./page_object_pattern.md
- WebPage API (direct alternative): ./webpage_api.md
- Runnable example: ../../tests/test_itempage_field.py
