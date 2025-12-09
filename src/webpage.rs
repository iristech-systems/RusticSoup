use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use scraper::{Html, Selector, ElementRef};
use std::collections::HashMap;

/// High-level abstraction for parsed HTML pages with metadata and structured access.
///
/// WebPage provides a powerful, BeautifulSoup-like interface for HTML parsing and data extraction.
/// Similar to web-poet's WebPage, it combines the parsed HTML document with metadata like URL
/// and custom attributes for comprehensive page representation.
///
/// # Arguments
///
/// * `html` - HTML string to parse
/// * `url` - Optional URL of the page (used for absolute URL resolution)
/// * `metadata` - Optional dictionary of custom metadata (headers, timestamps, etc.)
///
/// # Examples
///
/// ```python
/// from rusticsoup import WebPage
///
/// # Basic usage
/// page = WebPage(html_string)
///
/// # With URL and metadata
/// page = WebPage(
///     html_string,
///     url="https://example.com/product/123",
///     metadata={"fetch_time": "2024-01-01", "status": "200"}
/// )
///
/// # Extract data
/// title = page.text("h1.title")
/// links = page.attr_all("a", "href")
/// prices = page.text_all(".price")
///
/// # Structured extraction
/// data = page.extract({
///     'title': 'h1',
///     'price': '.price',
///     'image': 'img@src'
/// })
/// ```
#[pyclass(unsendable)]
#[derive(Clone)]
pub struct WebPage {
    html: Html,
    url: Option<String>,
    metadata: HashMap<String, String>,
}

#[pymethods]
impl WebPage {
    /// Create a new WebPage from HTML string
    #[new]
    #[pyo3(signature = (html, url=None, metadata=None))]
    pub fn new(
        html: &str,
        url: Option<String>,
        metadata: Option<HashMap<String, String>>,
    ) -> Self {
        Self {
            html: Html::parse_document(html),
            url,
            metadata: metadata.unwrap_or_default(),
        }
    }

    /// Get the page URL.
    ///
    /// # Returns
    ///
    /// The page URL if provided, None otherwise
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Get page metadata as a dictionary.
    ///
    /// # Returns
    ///
    /// Dictionary containing all metadata key-value pairs
    #[getter]
    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        for (key, value) in &self.metadata {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }

    /// Select a single element using CSS selector and return its HTML.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string (e.g., "div.content", "#main")
    ///
    /// # Returns
    ///
    /// HTML string of the first matching element, or None if not found
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    pub fn css(&self, selector: &str) -> PyResult<Option<String>> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next().map(|elem| elem.html()))
    }

    /// Select all elements matching CSS selector and return their HTML.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// List of HTML strings for all matching elements
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    pub fn css_all(&self, py: Python, selector: &str) -> PyResult<PyObject> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        let list = PyList::empty_bound(py);
        for elem in self.html.select(&sel) {
            list.append(elem.html())?;
        }
        Ok(list.into())
    }

    /// Extract text content from the first element matching the CSS selector.
    ///
    /// Combines all text nodes within the element, joins with spaces, and trims whitespace.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// Extracted text content, or empty string if element not found
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// title = page.text("h1.title")
    /// description = page.text("div.description")
    /// ```
    pub fn text(&self, selector: &str) -> PyResult<String> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next()
            .map(|elem| elem.text().collect::<Vec<_>>().join(" ").trim().to_string())
            .unwrap_or_default())
    }

    /// Extract text content from all elements matching the CSS selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// List of text strings from all matching elements
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// all_prices = page.text_all(".price")
    /// all_headings = page.text_all("h2")
    /// ```
    pub fn text_all(&self, py: Python, selector: &str) -> PyResult<PyObject> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        let list = PyList::empty_bound(py);
        for elem in self.html.select(&sel) {
            let text = elem.text().collect::<Vec<_>>().join(" ").trim().to_string();
            list.append(text)?;
        }
        Ok(list.into())
    }

    /// Extract an attribute value from the first element matching the CSS selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    /// * `attribute` - Attribute name (e.g., "href", "src", "data-id")
    ///
    /// # Returns
    ///
    /// Attribute value if element and attribute exist, None otherwise
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// link = page.attr("a.product-link", "href")
    /// image = page.attr("img.main", "src")
    /// data_id = page.attr("div.item", "data-id")
    /// ```
    pub fn attr(&self, selector: &str, attribute: &str) -> PyResult<Option<String>> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next()
            .and_then(|elem| elem.value().attr(attribute).map(String::from)))
    }

    /// Extract an attribute value from all elements matching the CSS selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    /// * `attribute` - Attribute name
    ///
    /// # Returns
    ///
    /// List of attribute values from all matching elements that have the attribute
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// all_links = page.attr_all("a", "href")
    /// all_images = page.attr_all("img", "src")
    /// ```
    pub fn attr_all(&self, py: Python, selector: &str, attribute: &str) -> PyResult<PyObject> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        let list = PyList::empty_bound(py);
        for elem in self.html.select(&sel) {
            if let Some(attr_value) = elem.value().attr(attribute) {
                list.append(attr_value)?;
            }
        }
        Ok(list.into())
    }

    /// Extract structured data using field mappings.
    ///
    /// Provides a declarative way to extract multiple fields at once using a dictionary
    /// that maps field names to selector specifications.
    ///
    /// # Arguments
    ///
    /// * `field_mappings` - Dictionary mapping field names to selector specs
    ///
    /// # Selector Spec Format
    ///
    /// * `"selector"` - Extract text from selector
    /// * `"selector@attr"` - Extract attribute from selector
    /// * `"selector@get_all"` - Extract text from all matching elements
    /// * `"selector@attr@get_all"` - Extract attribute from all matching elements
    ///
    /// # Returns
    ///
    /// Dictionary with extracted values
    ///
    /// # Examples
    ///
    /// ```python
    /// data = page.extract({
    ///     'title': 'h1.title',
    ///     'price': '.price',
    ///     'link': 'a.product@href',
    ///     'all_images': 'img@src@get_all'
    /// })
    /// ```
    pub fn extract(&self, py: Python, field_mappings: &Bound<'_, PyDict>) -> PyResult<PyObject> {
        let result = PyDict::new_bound(py);

        for (field_name, selector_spec) in field_mappings.iter() {
            let field_name_str = field_name.extract::<String>()?;

            if let Ok(spec_str) = selector_spec.extract::<String>() {
                let value = self.extract_field(py, &spec_str)?;
                result.set_item(field_name_str, value)?;
            }
        }

        Ok(result.into())
    }

    /// Extract multiple items using a container selector and field mappings or ItemPage class.
    ///
    /// Finds all containers matching the selector, then extracts fields from each container.
    /// Perfect for extracting lists of products, reviews, or any repeated structure.
    ///
    /// # Arguments
    ///
    /// * `container_selector` - CSS selector for the container elements
    /// * `mapping_or_class` - Dictionary mapping field names to selector specs, OR an ItemPage class
    ///
    /// # Returns
    ///
    /// - If mapping is a dict: List of dictionaries with extracted fields
    /// - If mapping is an ItemPage class: List of ItemPage instances
    ///
    /// # Examples
    ///
    /// ```python
    /// # Dict-based extraction
    /// products = page.extract_all('.product', {
    ///     'name': 'h3.title',
    ///     'price': '.price',
    ///     'link': 'a@href',
    ///     'image': 'img@src'
    /// })
    /// # [{'name': '...', 'price': '...', ...}, {...}, ...]
    ///
    /// # ItemPage-based extraction
    /// class Review(ItemPage):
    ///     author = Field(css='.author')
    ///     rating = Field(css='.stars', attr='data-rating')
    ///     text = Field(css='.review-text')
    ///
    /// reviews = page.extract_all('.review', Review)
    /// # [Review(...), Review(...), ...]
    /// ```
    pub fn extract_all(&self, py: Python, container_selector: &str, mapping_or_class: &Bound<'_, PyAny>) -> PyResult<PyObject> {
        let list = PyList::empty_bound(py);

        let container_sel = Selector::parse(container_selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid container selector: {}", container_selector)
            ))?;

        // Check if mapping_or_class is a dict or a class
        if let Ok(field_mappings) = mapping_or_class.downcast::<PyDict>() {
            // Original dict-based extraction
            for container in self.html.select(&container_sel) {
                let item = self.extract_from_element(py, &container, field_mappings)?;
                list.append(item)?;
            }
        } else {
            // Assume it's an ItemPage class - extract using class instantiation
            for container in self.html.select(&container_sel) {
                // Create a WebPage from the container's HTML
                let container_html = container.html();
                let container_page = WebPage::new(&container_html, self.url.clone(), None);

                // Instantiate the ItemPage class with the container WebPage
                let instance = mapping_or_class.call1((container_page,))?;
                list.append(instance)?;
            }
        }

        Ok(list.into())
    }

    /// Get the raw HTML content of the entire page.
    ///
    /// # Returns
    ///
    /// Complete HTML document as a string
    pub fn html(&self) -> String {
        self.html.html()
    }

    /// Check if the selector matches any elements in the page.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// True if at least one element matches, False otherwise
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// if page.has(".out-of-stock"):
    ///     print("Product unavailable")
    /// ```
    pub fn has(&self, selector: &str) -> PyResult<bool> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next().is_some())
    }

    /// Count the number of elements matching the selector.
    ///
    /// # Arguments
    ///
    /// * `selector` - CSS selector string
    ///
    /// # Returns
    ///
    /// Number of matching elements
    ///
    /// # Raises
    ///
    /// * `ValueError` - If the CSS selector is invalid
    ///
    /// # Examples
    ///
    /// ```python
    /// review_count = page.count(".review")
    /// image_count = page.count("img")
    /// ```
    pub fn count(&self, selector: &str) -> PyResult<usize> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).count())
    }

    /// Resolve a relative URL to an absolute URL using the page's base URL.
    ///
    /// If the input URL is already absolute (starts with http:// or https://),
    /// returns it unchanged. Otherwise, combines with the page's URL.
    ///
    /// # Arguments
    ///
    /// * `relative_url` - URL to resolve (can be absolute, root-relative, or path-relative)
    ///
    /// # Returns
    ///
    /// Absolute URL
    ///
    /// # Examples
    ///
    /// ```python
    /// page = WebPage(html, url="https://example.com/products/123")
    ///
    /// # Root-relative URL
    /// abs_url = page.absolute_url("/images/photo.jpg")
    /// # Returns: "https://example.com/images/photo.jpg"
    ///
    /// # Path-relative URL
    /// abs_url = page.absolute_url("../other")
    /// # Returns: "https://example.com/products/../other"
    ///
    /// # Already absolute
    /// abs_url = page.absolute_url("https://other.com/page")
    /// # Returns: "https://other.com/page"
    /// ```
    pub fn absolute_url(&self, relative_url: &str) -> PyResult<String> {
        if relative_url.starts_with("http://") || relative_url.starts_with("https://") {
            return Ok(relative_url.to_string());
        }

        if let Some(base_url) = &self.url {
            // Simple URL joining - in production you'd use url crate
            if relative_url.starts_with('/') {
                // Extract base domain
                if let Some(domain_end) = base_url.find("://").and_then(|i| base_url[i+3..].find('/').map(|j| i+3+j)) {
                    return Ok(format!("{}{}", &base_url[..domain_end], relative_url));
                } else {
                    return Ok(format!("{}{}", base_url, relative_url));
                }
            } else {
                // Relative to current path
                if let Some(last_slash) = base_url.rfind('/') {
                    return Ok(format!("{}/{}", &base_url[..last_slash], relative_url));
                }
            }
        }

        Ok(relative_url.to_string())
    }

    /// String representation
    fn __repr__(&self) -> String {
        format!(
            "WebPage(url={:?}, metadata_keys={})",
            self.url,
            self.metadata.len()
        )
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }
}

impl WebPage {
    /// Internal helper to extract field based on spec string
    fn extract_field(&self, py: Python, spec: &str) -> PyResult<PyObject> {
        let (selector, extraction_type) = parse_field_spec(spec)?;

        match extraction_type {
            FieldType::Text => {
                Ok(self.text(&selector)?.into_py(py))
            }
            FieldType::TextAll => {
                self.text_all(py, &selector)
            }
            FieldType::Attribute(attr) => {
                Ok(self.attr(&selector, &attr)?.into_py(py))
            }
            FieldType::AttributeAll(attr) => {
                self.attr_all(py, &selector, &attr)
            }
        }
    }

    /// Internal helper to extract from a specific element
    fn extract_from_element(
        &self,
        py: Python,
        element: &ElementRef,
        field_mappings: &Bound<'_, PyDict>,
    ) -> PyResult<PyObject> {
        use crate::page_object::Field;

        let result = PyDict::new_bound(py);
        let elem_html = Html::parse_fragment(&element.html());

        for (field_name, selector_spec) in field_mappings.iter() {
            let field_name_str = field_name.extract::<String>()?;

            // Check if selector_spec is a Field object
            if let Ok(field) = selector_spec.downcast::<Field>() {
                // Create a WebPage from the element HTML and use Field.extract
                let container_html = element.html();
                let container_page = WebPage::new(&container_html, self.url.clone(), None);
                let value = field.borrow().extract(py, &container_page)?;
                result.set_item(field_name_str, value)?;
            } else if let Ok(spec_str) = selector_spec.extract::<String>() {
                // Original string-based extraction
                let (selector, extraction_type) = parse_field_spec(&spec_str)?;

                let sel = Selector::parse(&selector)
                    .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Invalid selector: {}", selector)
                    ))?;

                let value = match extraction_type {
                    FieldType::Text => {
                        elem_html.select(&sel).next()
                            .map(|e| e.text().collect::<Vec<_>>().join(" ").trim().to_string())
                            .unwrap_or_default()
                            .into_py(py)
                    }
                    FieldType::TextAll => {
                        let list = PyList::empty_bound(py);
                        for e in elem_html.select(&sel) {
                            list.append(e.text().collect::<Vec<_>>().join(" ").trim().to_string())?;
                        }
                        list.into()
                    }
                    FieldType::Attribute(attr) => {
                        elem_html.select(&sel).next()
                            .and_then(|e| e.value().attr(&attr).map(String::from))
                            .unwrap_or_default()
                            .into_py(py)
                    }
                    FieldType::AttributeAll(attr) => {
                        let list = PyList::empty_bound(py);
                        for e in elem_html.select(&sel) {
                            if let Some(attr_val) = e.value().attr(&attr) {
                                list.append(attr_val)?;
                            }
                        }
                        list.into()
                    }
                };

                result.set_item(field_name_str, value)?;
            }
        }

        Ok(result.into())
    }
}

enum FieldType {
    Text,
    TextAll,
    Attribute(String),
    AttributeAll(String),
}

/// Parse field specification string
/// Examples:
///   "h1" -> (h1, Text)
///   "h1@get_all" -> (h1, TextAll)
///   "a@href" -> (a, Attribute(href))
///   "img@src@get_all" -> (img, AttributeAll(src))
fn parse_field_spec(spec: &str) -> PyResult<(String, FieldType)> {
    let parts: Vec<&str> = spec.split('@').collect();

    match parts.len() {
        1 => {
            // Just selector, extract text
            Ok((parts[0].to_string(), FieldType::Text))
        }
        2 => {
            // selector@attr or selector@get_all
            if parts[1] == "get_all" {
                Ok((parts[0].to_string(), FieldType::TextAll))
            } else {
                Ok((parts[0].to_string(), FieldType::Attribute(parts[1].to_string())))
            }
        }
        3 => {
            // selector@attr@get_all
            if parts[2] == "get_all" {
                Ok((parts[0].to_string(), FieldType::AttributeAll(parts[1].to_string())))
            } else {
                Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid field spec: {}", spec)
                ))
            }
        }
        _ => {
            Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid field spec: {}", spec)
            ))
        }
    }
}
