# Containers, Mappings, and Structured Extraction

This guide explains the "container + mapping" pattern used across RusticSoup in both the WebPage API and the universal extraction functions. If you come from BeautifulSoup where you often loop manually over elements, this pattern replaces loops and nested `select` calls with a declarative, single-shot extraction.

- Container: a CSS selector that groups repeated blocks (e.g., a product card, a table row, a search result item).
- Mapping: a dictionary that maps output field names to extraction rules, using a concise selector syntax.

Works with:
- WebPage.extract(mapping) — extract one item from the whole page.
- WebPage.extract_all(container, mapping) — extract many items inside a container.
- rusticsoup.extract_data(html, container, mapping) — universal batch extraction.
- rusticsoup.extract_data_bulk(pages, container, mapping) — parallel version for many pages.

## Quick examples

### 1) Single item (no container) with WebPage.extract

```python
from rusticsoup import WebPage

page = WebPage(html)
product = page.extract({
    "title": "h1.product-title",
    "price": ".price",
    "url": "a.buy@href",
    "image": "img@src"
})
```

### 2) Repeated items with container + mapping

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://shop.example.com")
products = page.extract_all("div.product", {
    "name": "h2",
    "price": ".price",
    "url": "a@href",
    "image": "img@src"
})

# Optional post-processing (e.g., make URLs absolute)
for p in products:
    p["url"] = page.absolute_url(p["url"]) if p["url"] else None
    p["image"] = page.absolute_url(p["image"]) if p["image"] else None
```

### 3) Universal extraction (no WebPage object)

```python
import rusticsoup

field_mappings = {
    "name": "h3",
    "price": "span.price",
    "url": "a@href",
}

rows = rusticsoup.extract_data(html, "div.card", field_mappings)
```

## Mapping syntax

Inside a mapping, the value (right-hand side) is a compact instruction that tells RusticSoup what to extract for each key:

- "selector" → extract the text content of the first matching element
- "selector@attr" → extract attribute `attr` from the first match
- "selector@get_all" → extract text content for all matches (list)
- "selector@attr@get_all" → extract attribute for all matches (list)

Examples:

```python
{
    "title": "h1",               # text
    "price": ".price",          # text
    "link": "a@href",           # attribute
    "images": "img@src@get_all" # list of attributes
}
```

Notes:
- If a selector does not match, RusticSoup returns an empty string for text/attr and an empty list for `get_all` (see tests for exact behavior). Handle missing values as needed.
- Attribute names are free-form: `@href`, `@src`, `@alt`, `@data-id`, etc.

## Choosing the right entry point

- Use `WebPage.extract(mapping)` when you need a single record from a page (e.g., article details page).
- Use `WebPage.extract_all(container, mapping)` for lists/grids/tables (search results, product grids, rows).
- Use `rusticsoup.extract_data(html, container, mapping)` as a low-ceremony function that performs container + mapping extraction in one call.
- Use `rusticsoup.extract_data_bulk(pages, container, mapping)` for parallel extraction across many HTML documents.

## Real-world patterns

### Products grid

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://example.com")
products = page.extract_all(".product-card", {
    "title": "h2",
    "price": ".price",
    "url": "a@href",
    "image": "img@src",
    "tags": ".tag@get_all"
})
```

### Search results

```python
results = page.extract_all(".result", {
    "title": "h3 a",
    "url": "h3 a@href",
    "snippet": ".description",
    "price": ".price"  # optional, may be missing
})
```

### Table rows

```python
rows = page.extract_all("table.data tbody tr", {
    "name": "td.name",
    "age": "td.age",
    "city": "td.city"
})
# Convert types after extraction
for r in rows:
    r["age"] = int(r["age"]) if r["age"] else None
```

### Nested blocks (compose keys)

Nested data modeling is easy by post-processing the flat result, or by using multiple passes:

```python
cards = page.extract_all(".card", {
    "title": ".title",
    "price": ".price",
    "image": "img@src",
    "tag_list": ".tags a@get_all"
})

# Post-process into nested structure
for c in cards:
    c["tags"] = c.pop("tag_list", [])
```

## PageObject pattern vs mappings

When using `Field` inside `ItemPage` classes, the attribute names on the class play the role of the mapping keys, and the `Field` parameters (`css`, `attr`, `get_all`) encode the extraction rule:

```python
from rusticsoup_helpers import ItemPage
from rusticsoup import Field, WebPage

class Product(ItemPage):
    title = Field(css="h1.product-title")          # key: title
    link = Field(css="a.buy", attr="href")        # key: link
    images = Field(css="img.gallery", attr="src", get_all=True)  # key: images

page = WebPage(html)
prod = Product(page)
print(prod.to_dict())  # {'title': '...', 'link': '...', 'images': ['...']}
```

So, PageObjects are a declarative, typed way to define the same information you would otherwise place in a mapping.

## Pitfalls and best practices

1) Use specific selectors
- Prefer `.product-card h2` over just `h2` to avoid accidental matches.

2) Choose text vs attribute carefully
- If you want the URL, use `@href`. If you want link text, omit `@href`.

3) Use `get_all` for lists
- Make it explicit when you need multiple items. For attributes: `"img@src@get_all"`.

4) Handle missing fields gracefully
- Some items may not have a price or link. Use empty checks or defaults after extraction.

5) Batch extraction where possible
- `extract()` and `extract_all()` perform fewer passes than many individual calls.

## From BeautifulSoup to RusticSoup

BS4 style (manual loops):

```python
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
products = []
for div in soup.select(".product"):
    title_el = div.select_one("h2")
    price_el = div.select_one(".price")
    link_el = div.select_one("a")
    products.append({
        "title": title_el.get_text(strip=True) if title_el else "",
        "price": price_el.get_text(strip=True) if price_el else "",
        "url": link_el.get("href") if link_el else "",
    })
```

RusticSoup style (declarative):

```python
from rusticsoup import WebPage
page = WebPage(html)
products = page.extract_all(".product", {
    "title": "h2",
    "price": ".price",
    "url": "a@href"
})
```

## API cheat sheet

- `WebPage.extract(mapping)` — one record, no container
- `WebPage.extract_all(container, mapping)` — many records in `container`
- `rusticsoup.extract_data(html, container, mapping)` — function shortcut
- `rusticsoup.extract_data_bulk(pages, container, mapping)` — parallel pages

## See also

- WebPage API: ./webpage_api.md
- Quick Start: ./quickstart.md
- Field Usage: ./field_usage.md
- PageObject Pattern: ./page_object_pattern.md
- Field Transform: ./field_transform.md
- Tests: ../..//test_webpage_api.py, ../..//test_field_usage.py, ../..//test_new_features.py
