use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyType};
use crate::webpage::WebPage;

/// Field descriptor for declarative data extraction from HTML pages.
///
/// Field provides a declarative way to extract data from HTML using CSS selectors
/// or XPath expressions. It supports attribute extraction, getting all matches,
/// default values, required fields, transformation functions, fallback selectors,
/// and structured list extraction.
///
/// # Arguments
///
/// * `css` - CSS selector string or list of selectors for fallback (e.g., "h1.title", ["h1.title", "h1"])
/// * `xpath` - XPath expression (not yet implemented)
/// * `attr` - Attribute to extract (e.g., "href", "src", "data-id")
/// * `get_all` - Extract from all matching elements instead of just the first
/// * `default` - Default value if extraction fails or element not found
/// * `required` - Whether the field is required (raises error if not found)
/// * `transform` - Function or list of functions to transform extracted value
/// * `container` - Container selector for list extraction with mapping
/// * `mapping` - Field mappings dict for structured list extraction
///
/// # Examples
///
/// ```python
/// from rusticsoup import Field, WebPage
///
/// # Simple text extraction
/// title = Field(css="h1.title")
///
/// # Fallback selectors - tries each until one matches
/// price = Field(css=["span.price", "div.price", ".price"])
///
/// # Attribute extraction
/// link = Field(css="a.product-link", attr="href")
///
/// # Extract all matching elements
/// all_prices = Field(css=".price", get_all=True)
///
/// # With transformation
/// price = Field(
///     css=".price",
///     transform=lambda s: float(s.replace("$", "").replace(",", ""))
/// )
///
/// # List extraction with mapping
/// offers = Field(
///     container='div.offer',
///     mapping={
///         'title': 'h3',
///         'price': '.price',
///         'link': 'a@href'
///     }
/// )
/// ```
#[pyclass]
pub struct Field {
    css: Option<PyObject>,  // Can be string or list of strings
    xpath: Option<String>,
    attr: Option<String>,
    get_all: bool,
    default: Option<String>,
    required: bool,
    transform: Option<PyObject>,
    container: Option<String>,  // For list extraction
    mapping: Option<PyObject>,  // Dict for structured extraction
}

#[pymethods]
impl Field {
    #[new]
    #[pyo3(signature = (css=None, xpath=None, attr=None, get_all=false, default=None, required=true, transform=None, container=None, mapping=None))]
    pub fn new(
        css: Option<PyObject>,
        xpath: Option<String>,
        attr: Option<String>,
        get_all: bool,
        default: Option<String>,
        required: bool,
        transform: Option<PyObject>,
        container: Option<String>,
        mapping: Option<PyObject>,
    ) -> Self {
        Self {
            css,
            xpath,
            attr,
            get_all,
            default,
            required,
            transform,
            container,
            mapping,
        }
    }

    /// Extract value from a WebPage based on this field's configuration.
    ///
    /// Processes the field's selector (CSS or XPath), extracts the value,
    /// and applies any transformation functions. Supports fallback selectors
    /// and container+mapping for list extraction.
    ///
    /// # Arguments
    ///
    /// * `page` - WebPage object to extract data from
    ///
    /// # Returns
    ///
    /// Extracted and transformed value (str, list, or custom type from transform)
    ///
    /// # Raises
    ///
    /// * `ValueError` - If field has no selector or selector is invalid
    /// * `NotImplementedError` - If using XPath (not yet supported)
    pub fn extract(&self, py: Python, page: &WebPage) -> PyResult<PyObject> {
        // Handle container + mapping extraction (list of dicts)
        if let (Some(container), Some(mapping)) = (&self.container, &self.mapping) {
            let mapping_dict = mapping.downcast_bound::<PyDict>(py)
                .map_err(|_| PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "mapping must be a dictionary"
                ))?;
            return page.extract_all(py, container, mapping_dict);
        }

        let mut value = if let Some(css_obj) = &self.css {
            // Try to extract as list of selectors (fallback)
            if let Ok(css_list) = css_obj.downcast_bound::<PyList>(py) {
                self.extract_with_fallback(py, page, css_list)?
            }
            // Try as single string selector
            else if let Ok(css_str) = css_obj.extract::<String>(py) {
                let spec = self.build_spec(&css_str);
                self.extract_with_spec(py, page, &spec)?
            } else {
                return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "css must be a string or list of strings"
                ));
            }
        } else if let Some(_xpath) = &self.xpath {
            // XPath support would go here
            return Err(PyErr::new::<pyo3::exceptions::PyNotImplementedError, _>(
                "XPath support not yet implemented"
            ));
        } else if self.container.is_some() {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Field with container requires mapping parameter"
            ));
        } else {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Field must have either css, xpath, or container+mapping"
            ));
        };

        // Apply transforms if provided
        if let Some(transform) = &self.transform {
            value = self.apply_transforms(py, value, transform)?;
        }

        Ok(value)
    }

    fn __repr__(&self) -> String {
        format!(
            "Field(css={:?}, attr={:?}, get_all={})",
            self.css, self.attr, self.get_all
        )
    }
}

impl Field {
    /// Apply transform functions to the extracted value
    /// If transform is a list, apply each callable in order
    /// If transform is a single callable, apply it once
    fn apply_transforms(&self, py: Python, mut value: PyObject, transform: &PyObject) -> PyResult<PyObject> {
        // Check if transform is a list of callables
        if let Ok(transform_list) = transform.downcast_bound::<PyList>(py) {
            // Apply each transform in order
            for transform_fn in transform_list.iter() {
                if transform_fn.is_callable() {
                    value = transform_fn.call1((value,))?.into();
                } else {
                    return Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                        "All items in transform list must be callable"
                    ));
                }
            }
            Ok(value)
        } else if transform.bind(py).is_callable() {
            // Single callable
            Ok(transform.call1(py, (value,))?.into())
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "transform must be a callable or list of callables"
            ))
        }
    }

    /// Try multiple selectors in order until one succeeds
    fn extract_with_fallback(&self, py: Python, page: &WebPage, selectors: &Bound<'_, PyList>) -> PyResult<PyObject> {
        for selector_obj in selectors.iter() {
            if let Ok(selector_str) = selector_obj.extract::<String>() {
                let spec = self.build_spec(&selector_str);

                // Try to extract with this selector
                match self.extract_with_spec(py, page, &spec) {
                    Ok(value) => {
                        // Check if we got a non-empty result
                        // For strings, check if non-empty
                        if let Ok(s) = value.extract::<String>(py) {
                            if !s.is_empty() {
                                return Ok(value);
                            }
                        }
                        // For lists, check if non-empty
                        else if let Ok(list) = value.downcast_bound::<PyList>(py) {
                            if list.len() > 0 {
                                return Ok(value);
                            }
                        }
                        // For other types, assume valid
                        else if !value.is_none(py) {
                            return Ok(value);
                        }
                    }
                    Err(_) => {
                        // This selector failed, try next one
                        continue;
                    }
                }
            }
        }

        // All selectors failed, return default or empty
        if let Some(default) = &self.default {
            Ok(default.clone().into_py(py))
        } else if self.get_all {
            Ok(PyList::empty_bound(py).into())
        } else {
            Ok("".into_py(py))
        }
    }

    fn build_spec(&self, selector: &str) -> String {
        let mut spec = selector.to_string();

        if let Some(attr) = &self.attr {
            spec.push('@');
            spec.push_str(attr);
        }

        if self.get_all {
            spec.push_str("@get_all");
        }

        spec
    }

    fn extract_with_spec(&self, py: Python, page: &WebPage, spec: &str) -> PyResult<PyObject> {
        // Parse the spec and extract accordingly
        let parts: Vec<&str> = spec.split('@').collect();

        match parts.len() {
            1 => {
                // Just text
                if self.get_all {
                    page.text_all(py, parts[0])
                } else {
                    Ok(page.text(parts[0])?.into_py(py))
                }
            }
            2 => {
                if parts[1] == "get_all" {
                    page.text_all(py, parts[0])
                } else {
                    // Attribute extraction
                    if self.get_all {
                        page.attr_all(py, parts[0], parts[1])
                    } else {
                        Ok(page.attr(parts[0], parts[1])?.into_py(py))
                    }
                }
            }
            3 => {
                // selector@attr@get_all
                if parts[2] == "get_all" {
                    page.attr_all(py, parts[0], parts[1])
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
}

/// Base class for declarative page object models.
///
/// PageObject provides a structured way to extract data from web pages using
/// Field descriptors. Similar to web-poet's ItemPage pattern, it allows you
/// to define extraction logic as class attributes.
///
/// # Examples
///
/// ```python
/// from rusticsoup import Field, PageObject, WebPage
///
/// class ProductPage(PageObject):
///     title = Field(css="h1.product-title")
///     price = Field(css=".price", transform=extract_price)
///     image = Field(css="img.product-image", attr="src")
///     description = Field(css=".description")
///
/// # Usage
/// page = WebPage(html, url="https://example.com/product")
/// product = ProductPage(page)
/// print(product.title)  # Auto-extracted
/// print(product.price)  # Transformed value
/// ```
#[pyclass(subclass)]
pub struct PageObject {
    #[pyo3(get)]
    page: Py<WebPage>,
}

#[pymethods]
impl PageObject {
    #[new]
    pub fn new(page: Py<WebPage>) -> Self {
        Self { page }
    }

    /// Create a PageObject instance and extract all fields from the page.
    ///
    /// This class method inspects the class for Field descriptors and
    /// automatically extracts all defined fields from the provided page.
    ///
    /// # Arguments
    ///
    /// * `page` - WebPage object containing the HTML to extract from
    ///
    /// # Returns
    ///
    /// PageObject instance with all fields extracted
    #[classmethod]
    pub fn from_page(_cls: &Bound<'_, PyType>, py: Python, page: &WebPage) -> PyResult<PyObject> {
        // This will be called from Python to extract all fields
        // The actual field extraction happens in Python using descriptors
        Ok(page.clone().into_py(py))
    }

    /// Convert PageObject to a dictionary representation.
    ///
    /// Returns a dict containing all extracted field values.
    ///
    /// # Returns
    ///
    /// Dictionary with field names as keys and extracted values
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new_bound(py);

        // Return the page as a dict representation
        // The actual field extraction will be done in Python
        dict.set_item("_page_url", self.page.bind(py).borrow().url())?;

        Ok(dict)
    }

    fn __repr__(&self) -> String {
        "PageObject()".to_string()
    }
}

/// Processor decorator for defining extraction logic as functions.
///
/// Processor allows you to define extraction logic as decorated functions
/// that receive a WebPage and return extracted data. This is an alternative
/// to the Field descriptor approach.
///
/// # Examples
///
/// ```python
/// from rusticsoup import processor, WebPage
///
/// @processor()
/// def extract_product_data(page: WebPage):
///     return {
///         'title': page.text('h1'),
///         'price': page.text('.price'),
///         'images': page.attr_all('img', 'src')
///     }
///
/// # Usage
/// page = WebPage(html)
/// data = extract_product_data(page)
/// ```
#[pyclass]
pub struct Processor {
    func: PyObject,
    input_type: Option<String>,
}

#[pymethods]
impl Processor {
    #[new]
    #[pyo3(signature = (func, input_type=None))]
    pub fn new(func: PyObject, input_type: Option<String>) -> Self {
        Self { func, input_type }
    }

    /// Call the processor function with a WebPage.
    ///
    /// # Arguments
    ///
    /// * `page` - WebPage object to process
    ///
    /// # Returns
    ///
    /// Result from the processor function
    pub fn __call__(&self, py: Python, page: Py<WebPage>) -> PyResult<PyObject> {
        self.func.call1(py, (page,))
    }

    fn __repr__(&self) -> String {
        format!("Processor(input_type={:?})", self.input_type)
    }
}

/// Create a processor decorator for extraction functions.
///
/// # Arguments
///
/// * `input_type` - Optional type hint for the input (for documentation)
///
/// # Returns
///
/// ProcessorDecorator that can be used to wrap extraction functions
///
/// # Examples
///
/// ```python
/// @processor()
/// def extract_reviews(page):
///     return page.extract_all('.review', {
///         'author': '.author',
///         'rating': '.rating@data-value',
///         'text': '.review-text'
///     })
/// ```
#[pyfunction]
#[pyo3(signature = (input_type=None))]
pub fn processor(input_type: Option<String>) -> PyResult<ProcessorDecorator> {
    Ok(ProcessorDecorator { input_type })
}

#[pyclass]
pub struct ProcessorDecorator {
    input_type: Option<String>,
}

#[pymethods]
impl ProcessorDecorator {
    fn __call__(&self, _py: Python, func: PyObject) -> PyResult<Processor> {
        Ok(Processor::new(func, self.input_type.clone()))
    }
}

/// Extract all Field descriptors from a PageObject class into a dictionary.
///
/// This function inspects a PageObject class, finds all Field descriptors,
/// extracts their values from the provided WebPage, and returns them as a dict.
///
/// # Arguments
///
/// * `page` - WebPage object to extract from
/// * `page_object_class` - PageObject class with Field descriptors
///
/// # Returns
///
/// Dictionary with field names as keys and extracted values
///
/// # Examples
///
/// ```python
/// from rusticsoup import Field, extract_page_object, WebPage
///
/// class ProductPage:
///     title = Field(css="h1")
///     price = Field(css=".price")
///
/// page = WebPage(html)
/// data = extract_page_object(page, ProductPage)
/// # {'title': '...', 'price': '...'}
/// ```
// Add these imports
// Add KeyValue import
// Add KeyValue import
#[cfg(feature = "telemetry")]
use opentelemetry::{global, KeyValue, trace::{Tracer, TraceContextExt, Status}};

/// Extract all Field descriptors from a PageObject class into a dictionary.
///
/// This function inspects a PageObject class, finds all Field descriptors,
/// extracts their values from the provided WebPage, and returns them as a dict.
///
/// # Arguments
///
/// * `page` - WebPage object to extract from
/// * `page_object_class` - PageObject class with Field descriptors
///
/// # Returns
///
/// Dictionary with field names as keys and extracted values
///
/// # Examples
///
/// ```python
/// from rusticsoup import Field, extract_page_object, WebPage
///
/// class ProductPage:
///     title = Field(css="h1")
///     price = Field(css=".price")
///
/// page = WebPage(html)
/// data = extract_page_object(page, ProductPage)
/// # {'title': '...', 'price': '...'}
/// ```
#[pyfunction]
pub fn extract_page_object<'py>(
    py: Python<'py>,
    page: &WebPage,
    page_object_class: &Bound<'py, PyAny>,
) -> PyResult<Bound<'py, PyDict>> {
    #[cfg(feature = "telemetry")]
    {
        // Start page span using in_span to ensure it's ended correctly
        let tracer = global::tracer("rusticsoup");
        let class_name = page_object_class.getattr("__name__")?.extract::<String>()?;
        tracer.in_span("ItemPage.extract", |cx| {
            cx.span().set_attribute(KeyValue::new("page_object.class", class_name));
            
            // Get class fields
            let class_dict = page_object_class.getattr("__dict__")?;
            // mappingproxy cannot be downcast to PyDict, so we iterate using generic iterator
        
            let result = PyDict::new_bound(py);
        
            // Extract each field
            for key_res in class_dict.iter()? {
                let key = key_res?;
                let value = class_dict.get_item(&key)?;
                if let Ok(key_str) = key.extract::<String>() {
                    if !key_str.starts_with('_') {
                        // Check if it's a Field descriptor
                        if let Ok(field) = value.downcast::<Field>() {
                            // Start field span
                            let extracted_value = tracer.in_span("Field.extract", |cx| {
                                let span = cx.span();
                                span.set_attribute(KeyValue::new("field.name", key_str.clone()));
                                
                                let res = field.borrow().extract(py, page);
                                
                                match &res {
                                    Ok(val) => {
                                        // Get string representation for attribute
                                        let val_str = val.bind(py).str().map(|s| s.to_string()).unwrap_or_else(|_| "<???>".to_string());
                                        // Truncate if too long (optional but good practice)
                                        let display_val = if val_str.len() > 100 {
                                            format!("{}...", &val_str[..100])
                                        } else {
                                            val_str
                                        };
                                        span.set_attribute(KeyValue::new("field.value", display_val));
    
                                        // Helper to check if empty/falsy
                                        let is_empty = val.is_none(py) || 
                                                       val.extract::<String>(py).map(|s| s.is_empty()).unwrap_or(false) ||
                                                       val.downcast_bound::<PyList>(py).map(|l| l.len() == 0).unwrap_or(false);
                                        
                                        if is_empty {
                                            if field.borrow().required {
                                                span.set_status(Status::Error { description: "Field required but not found".into() });
                                            }
                                        } else {
                                            span.set_status(Status::Ok);
                                        }
                                    },
                                    Err(e) => {
                                        span.set_status(Status::Error { description: e.to_string().into() });
                                    }
                                }
                                res
                            })?;
                            result.set_item(key_str, extracted_value)?;
                        }
                    }
                }
            }
        
            Ok(result)
        })
    }
    
    #[cfg(not(feature = "telemetry"))]
    {
        // Non-telemetry fallback (original logic)
         // Get class fields
        let class_dict = page_object_class.getattr("__dict__")?;
        let result = PyDict::new_bound(py);
    
        // Extract each field
        for key_res in class_dict.iter()? {
            let key = key_res?;
            let value = class_dict.get_item(&key)?;
            if let Ok(key_str) = key.extract::<String>() {
                if !key_str.starts_with('_') {
                    // Check if it's a Field descriptor
                    if let Ok(field) = value.downcast::<Field>() {
                        let extracted_value = field.borrow().extract(py, page)?;
                        result.set_item(key_str, extracted_value)?;
                    }
                }
            }
        }
    
        Ok(result)
    }
}
