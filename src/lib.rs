/*!
# RusticSoup

Lightning-fast HTML parser and data extractor built in Rust.
A BeautifulSoup killer with browser-grade parsing performance.

## Features

- **Universal HTML extraction** - works with any website structure
- **Browser-grade parsing** - built on html5ever (used by Firefox/Servo)
- **CSS selectors** - full CSS selector support
- **Attribute extraction** - use `@attribute` syntax for href, src, etc.
- **Bulk processing** - parallel processing of multiple pages
- **2-10x faster** than BeautifulSoup for real-world scraping

## Quick Start

```python
import rusticsoup

# Parse any HTML structure
html = "<div class='item'><a href='/link'>Title</a><span>$99</span></div>"

# Universal extraction - works with ANY website
data = rusticsoup.extract_data(html, "div.item", {
    "title": "a",           # Text content
    "price": "span",        # Text content  
    "link": "a@href"        # Attribute extraction
})

# Result: [{"title": "Title", "price": "$99", "link": "/link"}]
```

## Core Functions

- `extract_data()` - Universal HTML data extraction
- `extract_data_bulk()` - Parallel processing of multiple pages
- `parse_html()` - Low-level HTML parsing and DOM access
- `bulk_parse_google_shopping()` - Optimized Google Shopping parser

*/

use pyo3::prelude::*;
use rayon::prelude::*;

mod errors;
mod encoding;
mod scraper;
mod bulk_parser;
mod universal_extractor;
mod bs4_api;

use pyo3::prelude::*;
use scraper::{WebScraper, Element, parse_html, extract, extract_all};
use bulk_parser::{parse_multiple_google_pages, bulk_parse_google_shopping, benchmark_bulk_parsing};
use universal_extractor::{extract_data, extract_data_bulk, extract_table_data};
use bs4_api::RusticSoup;

#[pymodule]
fn rusticsoup(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", "0.1.0")?;
    m.add("__doc__", "Lightning-fast HTML parser and data extractor - BeautifulSoup killer built in Rust")?;

    // Exceptions (exposed types)
    Python::with_gil(|py| -> PyResult<()> {
        m.add("RusticSoupError", py.get_type_bound::<errors::RusticSoupError>())?;
        m.add("HTMLParseError", py.get_type_bound::<errors::HTMLParseError>())?;
        m.add("SelectorError", py.get_type_bound::<errors::SelectorError>())?;
        m.add("EncodingError", py.get_type_bound::<errors::EncodingError>())?;
        Ok(())
    })?;
    
    // Universal extractors - the main API
    m.add_function(wrap_pyfunction!(extract_data, m)?)?;
    m.add_function(wrap_pyfunction!(extract_data_bulk, m)?)?;
    m.add_function(wrap_pyfunction!(extract_table_data, m)?)?;
    
    // Low-level HTML parsing
    m.add_class::<WebScraper>()?;
    m.add_class::<Element>()?;
    m.add_function(wrap_pyfunction!(parse_html, m)?)?;
    m.add_function(wrap_pyfunction!(extract, m)?)?;
    m.add_function(wrap_pyfunction!(extract_all, m)?)?;

    // BS4-like facade (early scaffold)
    m.add_class::<RusticSoup>()?;
    
    // Specialized bulk parsing (legacy/optimization)
    m.add_function(wrap_pyfunction!(parse_multiple_google_pages, m)?)?;
    m.add_function(wrap_pyfunction!(bulk_parse_google_shopping, m)?)?;
    m.add_function(wrap_pyfunction!(benchmark_bulk_parsing, m)?)?;
    
    Ok(())
}