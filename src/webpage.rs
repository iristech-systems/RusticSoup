use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use scraper::{Html, Selector, ElementRef};
use std::collections::HashMap;

/// WebPage - A high-level abstraction for parsed HTML pages
/// Similar to web-poet's WebPage, provides metadata and structured access to HTML
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

    /// Get the page URL
    #[getter]
    pub fn url(&self) -> Option<String> {
        self.url.clone()
    }

    /// Get page metadata
    #[getter]
    pub fn metadata(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        for (key, value) in &self.metadata {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }

    /// Select a single element using CSS selector
    pub fn css(&self, selector: &str) -> PyResult<Option<String>> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next().map(|elem| elem.html()))
    }

    /// Select all elements matching CSS selector
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

    /// Extract text from CSS selector
    pub fn text(&self, selector: &str) -> PyResult<String> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next()
            .map(|elem| elem.text().collect::<Vec<_>>().join(" ").trim().to_string())
            .unwrap_or_default())
    }

    /// Extract text from all matching elements
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

    /// Extract attribute from CSS selector
    pub fn attr(&self, selector: &str, attribute: &str) -> PyResult<Option<String>> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next()
            .and_then(|elem| elem.value().attr(attribute).map(String::from)))
    }

    /// Extract attribute from all matching elements
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

    /// Extract structured data using field mappings (like extract_data but on WebPage)
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

    /// Extract multiple items using container selector and field mappings
    pub fn extract_all(&self, py: Python, container_selector: &str, field_mappings: &Bound<'_, PyDict>) -> PyResult<PyObject> {
        let list = PyList::empty_bound(py);

        let container_sel = Selector::parse(container_selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid container selector: {}", container_selector)
            ))?;

        for container in self.html.select(&container_sel) {
            let item = self.extract_from_element(py, &container, field_mappings)?;
            list.append(item)?;
        }

        Ok(list.into())
    }

    /// Get raw HTML content
    pub fn html(&self) -> String {
        self.html.html()
    }

    /// Check if selector matches any elements
    pub fn has(&self, selector: &str) -> PyResult<bool> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).next().is_some())
    }

    /// Count matching elements
    pub fn count(&self, selector: &str) -> PyResult<usize> {
        let sel = Selector::parse(selector)
            .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid CSS selector: {}", selector)
            ))?;

        Ok(self.html.select(&sel).count())
    }

    /// Get absolute URL (resolve relative URLs)
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
        let result = PyDict::new_bound(py);
        let elem_html = Html::parse_fragment(&element.html());

        for (field_name, selector_spec) in field_mappings.iter() {
            let field_name_str = field_name.extract::<String>()?;

            if let Ok(spec_str) = selector_spec.extract::<String>() {
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
