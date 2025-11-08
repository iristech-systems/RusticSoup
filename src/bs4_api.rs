use pyo3::prelude::*;
use pyo3::types::PyType;

use crate::encoding::decode_bytes_to_string;
use crate::scraper::{WebScraper, Element};
use crate::scraper::parse_html;

/// BeautifulSoup-compatible HTML parser for easy migration.
///
/// RusticSoup provides a familiar API for users migrating from BeautifulSoup,
/// with find(), find_all(), and select() methods. Powered by Rust for speed.
///
/// # Examples
///
/// ```python
/// from rusticsoup import RusticSoup
///
/// soup = RusticSoup(html_string)
///
/// # BeautifulSoup-style API
/// title = soup.find("h1")
/// links = soup.find_all("a", limit=10)
///
/// # CSS selectors
/// products = soup.select(".product")
/// first_product = soup.select_one(".product")
///
/// # Get all text
/// text = soup.text
/// ```
#[pyclass(unsendable)]
pub struct RusticSoup {
    scraper: WebScraper,
}

#[pymethods]
impl RusticSoup {
    /// Create a new RusticSoup parser from HTML string.
    ///
    /// # Arguments
    ///
    /// * `html` - HTML string to parse
    ///
    /// # Returns
    ///
    /// RusticSoup instance ready for querying
    #[new]
    pub fn new(html: &str) -> PyResult<Self> {
        Ok(Self { scraper: parse_html(html) })
    }

    /// Create a RusticSoup parser from bytes.
    ///
    /// Decodes bytes as UTF-8 (with optional BOM handling).
    ///
    /// # Arguments
    ///
    /// * `data` - Bytes containing HTML
    ///
    /// # Returns
    ///
    /// RusticSoup instance
    #[classmethod]
    pub fn from_bytes(_cls: &Bound<PyType>, data: &[u8]) -> PyResult<Self> {
        let s = decode_bytes_to_string(data)?;
        Ok(Self { scraper: parse_html(&s) })
    }

    /// Select all elements matching the CSS selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// List of matching Element objects
    pub fn select(&self, selector: &str) -> PyResult<Vec<Element>> {
        self.scraper.select(selector)
    }

    /// Select the first element matching the CSS selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// First matching Element, or None if not found
    pub fn select_one(&self, selector: &str) -> PyResult<Option<Element>> {
        self.scraper.select_one(selector)
    }

    /// Find the first element by tag name (BeautifulSoup-compatible).
    ///
    /// # Arguments
    ///
    /// * `name` - Tag name to search for (e.g., "div", "a", "h1")
    ///
    /// # Returns
    ///
    /// First matching Element, or None if not found
    ///
    /// # Examples
    ///
    /// ```python
    /// title = soup.find("h1")
    /// link = soup.find("a")
    /// ```
    #[pyo3(signature = (name=None))]
    pub fn find(&self, name: Option<&str>) -> PyResult<Option<Element>> {
        let selector = name.unwrap_or("*");
        self.scraper.select_one(selector)
    }

    /// Find all elements by tag name (BeautifulSoup-compatible).
    ///
    /// # Arguments
    ///
    /// * `name` - Tag name to search for (defaults to all elements if None)
    /// * `limit` - Maximum number of results to return
    ///
    /// # Returns
    ///
    /// List of matching Elements
    ///
    /// # Examples
    ///
    /// ```python
    /// all_links = soup.find_all("a")
    /// first_10_divs = soup.find_all("div", limit=10)
    /// ```
    #[pyo3(signature = (name=None, limit=None))]
    pub fn find_all(&self, name: Option<&str>, limit: Option<usize>) -> PyResult<Vec<Element>> {
        let selector = name.unwrap_or("*");
        let mut elems = self.scraper.select(selector)?;
        if let Some(l) = limit {
            if elems.len() > l { elems.truncate(l); }
        }
        Ok(elems)
    }

    /// Get all text content from the document (whitespace-normalized).
    ///
    /// # Returns
    ///
    /// Cleaned text with normalized whitespace
    #[getter]
    pub fn text(&self) -> String {
        self.scraper.text()
    }
}
