# Fallback Selectors Guide

When sites vary their markup, `Field(css=[...])` lets you declare a list of fallback selectors. RusticSoup will try each selector in order and use the first one that returns a non-empty value. This page mirrors the patterns in `test_new_features.py` with shortened, copy‑pasteable examples.

## TL;DR
- Pass a list of CSS selectors to `Field(css=[...])`.
- Works for single values and with `get_all=True`.
- Combine with container + mapping for list extraction, or use `WebPage.extract_all` directly.

## 1) Single value with fallbacks
```python
from rusticsoup import WebPage, Field

html = """
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
"""

page = WebPage(html)

# Try these selectors in order until one produces a value
price_field = Field(css=[".price-new", ".price-old", ".sale-price"])

# Extract from each product by scoping a WebPage to that product's HTML
products = page.css_all(".product")
prices = []
for product_html in products:
    prices.append(price_field.extract(WebPage(product_html)))

print(prices)  # ['$99.99', '$149.99', '$79.99']
```

## 2) List extraction with `get_all=True` (fallback across variants)
```python
from rusticsoup import WebPage, Field

html = """
<span class="price-new">$10</span>
<span class="price-old">$12</span>
<span class="sale-price">$8</span>
"""

page = WebPage(html)
all_prices_field = Field(css=[".price-new", ".price-old", ".sale-price"], get_all=True)
print(all_prices_field.extract(page))  # ['$10', '$12', '$8']
```

## 3) Container + mapping as a Field
Pair fallbacks with a container to extract multiple items as a list of dicts.
```python
from rusticsoup import WebPage, Field

html = """
<div class="offers">
  <div class="offer"><div class="seller">Seller 1</div><span class="price">$99.99</span><a href="/offer1">View</a></div>
  <div class="offer"><div class="seller">Seller 2</div><span class="price">$95.99</span><a href="/offer2">View</a></div>
</div>
"""

page = WebPage(html)

mapping = {
    "seller": [".seller", ".merchant"],   # fallback inside mapping values is allowed
    "price": [".price", ".sale-price"],
    "link": "a@href",
}

offers_field = Field(container=".offer", mapping=mapping)
offers = offers_field.extract(page)
print(offers[0])  # {'seller': 'Seller 1', 'price': '$99.99', 'link': '/offer1'}
```

## 4) Alternative: use WebPage.extract_all directly
Everything above can also be expressed with `WebPage.extract_all` if you prefer a functional style.
```python
from rusticsoup import WebPage

html = """
<div class="offers">
  <div class="offer"><div class="seller">Seller 1</div><span class="price">$99.99</span><a href="/offer1">View</a></div>
  <div class="offer"><div class="seller">Seller 2</div><span class="price">$95.99</span><a href="/offer2">View</a></div>
</div>
"""

page = WebPage(html)
mapping = {"seller": [".seller", ".merchant"], "price": [".price", ".sale-price"], "link": "a@href"}
print(page.extract_all(".offer", mapping))
```

## BS4 vs RusticSoup (fallbacks)
```
# BeautifulSoup (conceptual): manual try/except or if/else across multiple classes
# Requires: pip install beautifulsoup4
#
# soup = BeautifulSoup(html, 'html.parser')
# prices = []
# for product in soup.select('.product'):
#     el = (product.select_one('.price-new') or
#           product.select_one('.price-old') or
#           product.select_one('.sale-price'))
#     prices.append(el.get_text(strip=True) if el else '')
```
```python
# RusticSoup: declarative fallbacks
from rusticsoup import Field, WebPage
html = """
<div class="product"><div class="price-new">$99.99</div></div>
<div class="product"><span class="price-old">$149.99</span></div>
<div class="product"><div class="sale-price">$79.99</div></div>
"""
price_field = Field(css=['.price-new', '.price-old', '.sale-price'])
prices = [price_field.extract(WebPage(p)) for p in WebPage(html).css_all('.product')]
```

## See Also
- WebPage API: ./webpage_api.md
- Field Usage: ./field_usage.md
- Containers & Mappings: ./containers_and_mappings.md
- Runnable examples in tests: ../../test_new_features.py
