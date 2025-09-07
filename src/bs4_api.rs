use pyo3::prelude::*;
use pyo3::types::PyType;

use crate::encoding::decode_bytes_to_string;
use crate::scraper::{WebScraper, Element};
use crate::scraper::parse_html;

/// A minimal BeautifulSoup-like facade to begin API alignment.
#[pyclass(unsendable)]
pub struct RusticSoup {
    scraper: WebScraper,
}

#[pymethods]
impl RusticSoup {
    /// Create from str or bytes. Bytes are decoded as UTF-8 with optional BOM for now.
    #[new]
    pub fn new(html: &str) -> PyResult<Self> {
        Ok(Self { scraper: parse_html(html) })
    }

    /// Alternative constructor from bytes (UTF-8/BOM only for now)
    #[classmethod]
    pub fn from_bytes(_cls: &Bound<PyType>, data: &[u8]) -> PyResult<Self> {
        let s = decode_bytes_to_string(data)?;
        Ok(Self { scraper: parse_html(&s) })
    }

    /// CSS select all (alias to underlying engine)
    pub fn select(&self, selector: &str) -> PyResult<Vec<Element>> {
        self.scraper.select(selector)
    }

    /// CSS select first (alias)
    pub fn select_one(&self, selector: &str) -> PyResult<Option<Element>> {
        self.scraper.select_one(selector)
    }

    /// Minimal find: finds by tag name using CSS translation; returns first match
    #[pyo3(signature = (name=None))]
    pub fn find(&self, name: Option<&str>) -> PyResult<Option<Element>> {
        let selector = name.unwrap_or("*");
        self.scraper.select_one(selector)
    }

    /// Minimal find_all: finds by tag name; optional limit truncation later can be added.
    #[pyo3(signature = (name=None, limit=None))]
    pub fn find_all(&self, name: Option<&str>, limit: Option<usize>) -> PyResult<Vec<Element>> {
        let selector = name.unwrap_or("*");
        let mut elems = self.scraper.select(selector)?;
        if let Some(l) = limit {
            if elems.len() > l { elems.truncate(l); }
        }
        Ok(elems)
    }

    /// Get all document text (whitespace-normalized)
    #[getter]
    pub fn text(&self) -> String {
        self.scraper.text()
    }
}
