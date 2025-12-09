# Changelog

All notable changes to RusticSoup will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2025-01-20

### Added

- **🛡️ Authenticated Telemetry**: Support for OTLP headers in `init_telemetry`
  - Pass custom headers (e.g., SigNoz/Jaeger auth tokens): `init_telemetry(headers={"signoz-access-token": "..."})`
  - Configurable OTLP endpoint support via explicit `endpoint` argument.

- **🚀 Flexible Telemetry Configuration**:
  - **Dual Mode**: Stream traces to console AND OTLP collector simultaneously.
  - **Zero-Cost Defaults**: Telemetry is opt-in at runtime; if not initialized, overhead is negligible.
  - **Feature Flag**: Added `telemetry` feature (enabled by default) to allow building ultra-light binaries if needed.

- **✨ Code Polish & IDE Support (Python 3.14 Ready)**:
  - **Type Stubs**: `__init__.pyi` fully aligned with implementation for perfect autocomplete.
  - **Docstrings**: Comprehensive Google-style docstrings for all exported members.
  - **Clean Builds**: Eliminated all standard Rust warnings and PyO3 false positives.
  - **Strict Typing**: Headers now enforced as `dict[str, str]` for type safety.

### Changed

- **Telemetry Initialization**: `init_telemetry` now accepts `headers` and `console` arguments.
- **Dependencies**: Downgraded `tonic` to 0.9 to resolve version conflicts with `opentelemetry-otlp` 0.14.

## [0.4.0] - 2025-01-09

### Added

- **🎯 ItemPage with extract_all()**: Major enhancement to extraction patterns
  - `WebPage.extract_all()` now accepts ItemPage classes in addition to dict mappings
  - Pass an ItemPage class: `page.extract_all('.offer', OfferClass)`
  - Returns list of ItemPage instances with all fields auto-extracted and transforms applied
  - Enables the cleanest possible extraction pattern with declarative field definitions

- **🔧 Field Objects in Mapping Dicts**: Per-field transforms in container+mapping
  - Field objects can now be used in mapping dicts (not just strings)
  - `Field(container='.offer', mapping={'title': Field(css='h3', transform=str.upper)})`
  - Each field gets its own transforms, fallback selectors, and configuration
  - Eliminates need for post-processing list comprehensions

### Changed

- **WebPage.extract_all() signature**: Now accepts `mapping_or_class: &Bound<'_, PyAny>` instead of `field_mappings: &Bound<'_, PyDict>`
  - Fully backward compatible - dict mappings still work exactly as before
  - Auto-detects whether argument is a dict or ItemPage class

- **Internal extract_from_element()**: Enhanced to support Field objects in mappings
  - Checks if mapping value is a Field object and calls `field.extract()` if so
  - Falls back to string-based extraction for backward compatibility

### Examples

```python
from rusticsoup import WebPage, Field, ItemPage

# Pattern 1: ItemPage with extract_all (cleanest!)
class ProductReview(ItemPage):
    author = Field(css='span.author', transform=str.strip)
    rating = Field(css='span.rating', transform=lambda s: float(s.split()[0]))
    text = Field(css='p.review-text', transform=str.strip)

page = WebPage(html)
reviews = page.extract_all('div.review', ProductReview)
# All transforms applied, returns list of ProductReview instances!

# Pattern 2: Field objects in mapping dict
offers_field = Field(
    container='.offer',
    mapping={
        'title': Field(css='h3', transform=str.upper),
        'price': Field(css='.price', transform=parse_price),
    }
)
offers = offers_field.extract(page)  # Transforms already applied!
```

### Benefits

- **Cleaner Code**: No more post-processing list comprehensions
- **Declarative**: All extraction logic lives with field definitions
- **Reusable**: Define ItemPage classes once, use everywhere
- **Type-Safe**: Access extracted data as attributes (`offer.price` not `offer['price']`)
- **Maintainable**: Field definitions are self-documenting

### Files Added

- `tests/test_itempage_extract_all.py`: Comprehensive test suite for new features
- `examples/google_shopping_itempage.py`: Real-world example using ItemPage pattern
- `ITEMPAGE_EXTRACT_ALL.md`: Complete documentation of new features

### Backward Compatibility

✅ 100% backward compatible - all existing code continues to work unchanged.
The new patterns are opt-in enhancements.

## [0.3.0] - 2025-01-08

### Added

- Documentation: New guides `help/fallback_selectors.md` and `docs/help/itempage_containers.md` that mirror `test_new_features.py` and `tests/test_itempage_field.py` with shortened, copy‑pasteable examples.
- Help Center: TOC updated to include the new guides.
- README: Links to the new guides under “Documentation & Examples”.
- Cross-links: Quickstart and Field Usage now point to the new guides.

- **🎯 Fallback Selectors**: Field now supports multiple CSS selectors with automatic fallback
  - Pass a list of selectors: `Field(css=["span.price", "div.price", ".price"])`
  - Tries each selector in order until one returns a non-empty result
  - Perfect for handling different site layouts with a single field definition

- **📋 Container+Mapping Extraction**: Field can now extract lists of structured data
  - New `container` and `mapping` parameters for list extraction
  - `Field(container='div.offer', mapping={'title': 'h3', 'price': '.price'})`
  - Returns list of dicts, one per container element
  - Ideal for extracting product grids, offers lists, reviews, etc.

- **📚 Complete IDE Support**: Comprehensive documentation for all APIs
  - Added Rust docstrings to all classes and methods (visible in Python help())
  - Created `.pyi` type stub files for full IDE autocomplete
  - Documentation includes parameters, return types, exceptions, and examples
  - Works with all Python IDEs (VS Code, PyCharm, etc.)

- **🔧 Data Extraction Utilities** (Python side):
  - `extractors.py`: Type conversion and common data extractors
    - `extract_price()`, `extract_int()`, `extract_bool()`
    - `extract_email()`, `extract_phone()`, `extract_url()`
    - `extract_date()` with common format support
  - `json_utils.py`: JSON extraction from HTML
    - `extract_json_ld()`: Extract JSON-LD structured data
    - `extract_json_from_script()`: Find JSON in script tags
    - `extract_json_variable()`: Extract JSON from JS variables
  - WebPage now has convenience methods: `page.json_ld()`, `page.json_in_script()`

### Changed

- **Field signature updated**: Now accepts `css` as string OR list
- **Field type**: `css` parameter changed from `Option<String>` to `Option<PyObject>` in Rust
- Updated `.pyi` stubs to reflect new Field capabilities

### Examples

```python
from rusticsoup import Field, WebPage, ItemPage

# Fallback selectors
price = Field(css=["span.price-new", "span.price-old", ".price"])

# Container + mapping for lists
offers = Field(
    container='div.offer',
    mapping={
        'seller': 'div.seller-name',
        'price': '.price',
        'link': 'a@href',
    }
)

# Use in ItemPage
class ProductPage(ItemPage):
    title = Field(css='h1')
    price = Field(css=["span.sale-price", "span.price"])
    offers = Field(container='div.offer', mapping={
        'seller': '.seller',
        'price': '.price'
    })
```

## [0.2.27] - 2025-11-07

### Fixed

- Fixed import system to properly export all classes and functions
- Resolved linting issues with explicit imports (ruff-compliant)
- Ensured `WebPage`, `Field`, `ItemPage`, and all helper classes are correctly importable
- All pre-commit hooks now pass

### Notes

- This is a bug-fix release ensuring all imports work correctly
- Fully backward compatible with 0.2.26
- All functionality verified and tested

## [0.2.26] - 2025-11-07

*Skipped - import issues discovered before wide distribution*

### Added

- **Built-in PageObject Helpers**: Core helper classes now included in the main package
  - `ItemPage` - Base class for auto-extracting page objects (no longer needs separate import)
  - `AutoExtract` - Decorator for auto-extraction
  - `page_object` - Function decorator for page objects
  - `PageObjectMeta` - Metaclass for Field collection
  - All helpers now available directly from `rusticsoup` import

### Changed

- **Dependency Updates**: Updated core dependencies for improved performance and compatibility
  - `scraper`: 0.22.0 → 0.24.0
  - `rayon`: 1.10.0 → 1.11.0
  - `selectors`: 0.25.0 → 0.26.0
  - Kept `pyo3` at 0.22 for stability (0.26 requires breaking changes)

### Fixed

- Fixed `Field` transform parameter to properly accept transform functions
- Resolved build caching issues that prevented proper module updates
- All existing tests continue to pass with updated dependencies

### Migration

**Before (0.2.2):**
```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage  # Separate file needed
```

**Now (0.2.27):**
```python
from rusticsoup import WebPage, Field, ItemPage  # All in one package!
```

## [0.2.25] - 2025-11-07

*Skipped - version was released early before helper integration was complete*

## [0.2.2] - 2025-01-07

### Added

- **Field Transform Feature**: Apply transformations to extracted data automatically
  - `Field(css, transform=callable)` - Single transform function
  - `Field(css, transform=[func1, func2, ...])` - Chain multiple transforms
  - Transforms execute in order after extraction
  - Works with text extraction, attribute extraction, and `get_all`
  - Integrates seamlessly with ItemPage pattern

### Documentation

- Added `FIELD_TRANSFORM.md` - Complete transform documentation
- Added `test_field_transform.py` - Comprehensive transform test suite (7 tests)
- Updated README with Field transform examples

### Features

**Transform Types:**
- Single callable: `transform=str.upper`
- Multiple callables: `transform=[str.strip, str.upper, lambda s: s.replace(" ", "_")]`
- Works with lists: `transform=lambda items: [i.upper() for i in items]`
- Works with attributes: `Field(css="a", attr="href", transform=normalize_url)`

**Integration:**
```python
class Article(ItemPage):
    title = Field(css="h1", transform=str.upper)
    author = Field(css=".author", transform=[str.strip, str.title])
    price = Field(css=".price", transform=[str.strip, lambda s: float(s.replace("$", ""))])
    tags = Field(css=".tag", get_all=True, transform=lambda t: [x.upper() for x in t])
```

### Benefits

- ✅ No manual post-processing needed
- ✅ Clean, declarative field definitions
- ✅ Reusable transform functions
- ✅ Chain transforms in order
- ✅ Works with all extraction types

## [0.2.1] - 2025-01-07

### Added

- **Field.extract() Method**: Fully exposed to Python
  - `Field.extract(page)` - Extract field value from WebPage
  - Enables reusable field extraction patterns
  - Works with all field types (text, attributes, get_all)

- **PageObject Pattern (Python-side)**: Auto-extracting page objects
  - `rusticsoup_helpers.py` - Helper module for PageObject pattern
  - `ItemPage` - Base class for auto-extracting page objects
  - `@page_object` decorator - Alternative page object creation
  - Define Fields once, auto-extract on instantiation
  - Access extracted data as attributes
  - `.to_dict()` method for easy serialization

### Documentation

- Added `FIELD_USAGE.md` - Complete Field usage guide
- Added `PAGE_OBJECT_PATTERN.md` - PageObject pattern documentation
- Added `test_field_usage.py` - Field extraction test suite
- Added `test_page_object_pattern.py` - PageObject pattern examples
- Added `FIELD_FIX_SUMMARY.md` - Field implementation details

### Fixed

- Field.extract() now properly exposed to Python (was in wrong impl block)
- PageObject auto-extraction now works correctly

### Examples

**Field Usage:**
```python
from rusticsoup import WebPage, Field

title_field = Field(css="h1")
tags_field = Field(css=".tag", get_all=True)

page = WebPage(html)
title = title_field.extract(page)  # "Article Title"
tags = tags_field.extract(page)     # ['Python', 'Rust']
```

**PageObject Pattern:**
```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

class Product(ItemPage):
    title = Field(css="h1")
    price = Field(css=".price")
    images = Field(css="img", attr="src", get_all=True)

# Auto-extract on instantiation!
page = WebPage(html)
product = Product(page)
print(product.title)   # Auto-extracted!
print(product.images)  # Auto-extracted!
```

## [0.2.0] - 2025-01-07

### Added - WebPage API (Major Feature Release)

🌟 **New WebPage API** - Inspired by [web-poet](https://github.com/scrapinghub/web-poet)

- **WebPage Class**: High-level abstraction for parsed HTML pages
  - `WebPage(html, url, metadata)` - Create page with URL and custom metadata
  - `text(selector)` / `text_all(selector)` - Extract text content
  - `attr(selector, attribute)` / `attr_all(selector, attribute)` - Extract attributes
  - `css(selector)` / `css_all(selector)` - Get HTML of elements
  - `has(selector)` - Check element existence
  - `count(selector)` - Count matching elements
  - `extract(mappings)` - Extract structured data
  - `extract_all(container, mappings)` - Extract multiple items
  - `absolute_url(url)` - Resolve relative URLs
  - `html()` - Get raw HTML content

- **Field Class**: Declarative field descriptors for PageObject pattern
  - `Field(css, attr, get_all, default, required)` - Define extraction fields
  - Support for CSS selectors and attributes
  - Batch extraction support with `get_all=True`

- **PageObject & Processor**: Base classes for page-based extraction
  - `PageObject` - Base class for item pages
  - `Processor` - Function decorator for custom extraction logic
  - `processor()` decorator function
  - `extract_page_object()` helper function

- **Enhanced Selector Syntax**:
  - `"selector@attr"` - Extract attribute
  - `"selector@get_all"` - Extract all text matches
  - `"selector@attr@get_all"` - Extract attribute from all matches

### Documentation

- Added comprehensive WebPage API documentation (`WEBPAGE_API.md`)
- Added quick start guide (`WEBPAGE_QUICKSTART.md`)
- Added complete test suite (`test_webpage_api.py`) with 9+ real-world examples
- Updated README with WebPage API examples and migration guides
- Added comparison with web-poet and BeautifulSoup

### Changed

- Updated package description to highlight WebPage API
- Added keywords: "webpage", "web-poet"
- Improved README structure with dual API showcase

### Performance

- WebPage API maintains 2-10x speed advantage over BeautifulSoup
- No async overhead - synchronous API is fast enough due to Rust implementation
- Memory efficient with html5ever parser

### Examples

See new documentation for complete examples:
- E-commerce product scraping
- News article extraction
- Search results parsing
- Table data extraction
- Google Shopping-like sites
- Amazon-like product pages

## [0.1.0] - 2024-09-09

### Added - Initial Release

- **Universal Extraction API**
  - `extract_data(html, container, mappings)` - Extract data from HTML
  - `extract_data_bulk(pages, container, mappings)` - Parallel batch processing
  - `extract_table_data(html, selector)` - Table extraction
  - `parse_html(html)` - Low-level HTML parsing

- **Core Features**
  - Browser-grade HTML parsing with html5ever
  - CSS selector support
  - Attribute extraction with `@` syntax
  - Parallel processing with Rayon
  - 2-10x faster than BeautifulSoup

- **Low-Level API**
  - `WebScraper` class for manual DOM traversal
  - `Element` class for element manipulation
  - Full CSS selector support

- **Error Handling**
  - `RusticSoupError` - Base exception
  - `HTMLParseError` - HTML parsing errors
  - `SelectorError` - CSS selector errors
  - `EncodingError` - Character encoding errors

- **CI/CD & Development**
  - Initial CI (build abi3 wheels, lint) and smoke tests
  - Pre-commit configuration (ruff, black)
  - Contribution docs, issue/PR templates, Code of Conduct, Dependabot

### Performance

- 2.1x faster than BeautifulSoup on Google Shopping pages
- 12x faster on product grid extraction
- Up to 100x faster with parallel batch processing

## [Unreleased]

### Planned Features

- XPath selector support
- Complete PageObject implementation with Python decorators
- Nested extraction support
- Custom field processors
- Type validation and conversion
- Selector result caching

---

## Migration Guide

### From 0.1.0 to 0.2.0

Version 0.2.0 is **100% backward compatible**. All existing code will continue to work.

**New recommended approach** for new projects:

```python
# Old way (still works)
import rusticsoup
products = rusticsoup.extract_data(html, ".product", {...})

# New way (recommended)
from rusticsoup import WebPage
page = WebPage(html)
products = page.extract_all(".product", {...})
```

**Benefits of WebPage API:**
- More Pythonic and object-oriented
- URL and metadata support
- More flexible extraction methods
- Compatible with web-poet patterns
- Better for complex scraping workflows

**When to use each API:**
- **WebPage API**: Single-page scraping, complex workflows, URL resolution needed
- **Universal API**: Batch processing, simple extraction, function-based preference

Both APIs have the same performance characteristics.

---

## Links

- [GitHub Repository](https://github.com/iristech-systems/RusticSoup)
- [WebPage API Documentation](WEBPAGE_API.md)
- [Quick Start Guide](WEBPAGE_QUICKSTART.md)
- [PyPI Package](https://pypi.org/project/rusticsoup/)
