use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyString};
use scraper::{Html, Selector, ElementRef};
use std::collections::HashMap;
use once_cell::sync::Lazy;
use std::sync::Mutex;
use ahash::AHashMap;
use sxd_document::parser;
use sxd_xpath::{evaluate_xpath, Value, nodeset::Node};

// Cache compiled selectors for performance
static SELECTOR_CACHE: Lazy<Mutex<AHashMap<String, Selector>>> = 
    Lazy::new(|| Mutex::new(AHashMap::new()));

#[pyclass(unsendable)]
pub struct WebScraper {
    document: Html,
}

#[pymethods]
impl WebScraper {
    #[new]
    fn new(html: &str) -> Self {
        WebScraper {
            document: Html::parse_document(html),
        }
    }

    /// Select all elements matching the CSS selector
    pub fn select(&self, selector: &str) -> PyResult<Vec<Element>> {
        let sel = get_or_compile_selector(selector)?;
        Ok(self.document.select(&sel)
            .map(|elem| Element::new(elem))
            .collect())
    }

    /// Select first element matching the CSS selector
    pub fn select_one(&self, selector: &str) -> PyResult<Option<Element>> {
        let sel = get_or_compile_selector(selector)?;
        Ok(self.document.select(&sel)
            .next()
            .map(|elem| Element::new(elem)))
    }

    /// Extract all text from the document
    pub fn text(&self) -> String {
        self.document.root_element()
            .text()
            .collect::<Vec<_>>()
            .join(" ")
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ")
    }

    /// Get the HTML of the entire document
    fn html(&self) -> String {
        self.document.html()
    }

    /// Extract all links (href attributes) from the document
    fn links(&self) -> PyResult<Vec<String>> {
        let sel = get_or_compile_selector("a[href]")?;
        Ok(self.document.select(&sel)
            .filter_map(|elem| elem.value().attr("href"))
            .map(|s| s.to_string())
            .collect())
    }

    /// Extract all image sources
    fn images(&self) -> PyResult<Vec<String>> {
        let sel = get_or_compile_selector("img[src]")?;
        Ok(self.document.select(&sel)
            .filter_map(|elem| elem.value().attr("src"))
            .map(|s| s.to_string())
            .collect())
    }

    /// Extract data using multiple selectors at once (for product grids)
    /// Supports both text and attribute extraction
    /// Use format "selector@attr" to extract attribute, e.g. "a@href"
    fn extract_grid(&self, py: Python, container_sel: &str, field_selectors: HashMap<String, String>) -> PyResult<PyObject> {
        let container = get_or_compile_selector(container_sel)?;
        let py_list = PyList::empty_bound(py);
        
        // Pre-compile selectors and parse attribute specifications
        let mut compiled_specs = HashMap::new();
        for (field, spec) in &field_selectors {
            if spec.contains('@') {
                // Format: "selector@attribute"
                let parts: Vec<&str> = spec.split('@').collect();
                if parts.len() == 2 {
                    let selector = get_or_compile_selector(parts[0])?;
                    compiled_specs.insert(field.clone(), (selector, Some(parts[1].to_string())));
                } else {
                    return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                        format!("Invalid attribute selector format: {}. Use 'selector@attribute'", spec)
                    ));
                }
            } else {
                // Regular text selector
                let selector = get_or_compile_selector(spec)?;
                compiled_specs.insert(field.clone(), (selector, None));
            }
        }
        
        for elem in self.document.select(&container) {
            let item_dict = PyDict::new_bound(py);
            let elem_html = Html::parse_fragment(&elem.html());
            
            for (field, (selector, attr_name)) in &compiled_specs {
                if let Some(found) = elem_html.select(selector).next() {
                    let value = if let Some(attr) = attr_name {
                        // Extract attribute
                        found.value().attr(attr).unwrap_or("").to_string()
                    } else {
                        // Extract text
                        found.text().collect::<Vec<_>>().join(" ").trim().to_string()
                    };
                    item_dict.set_item(field.as_str(), value)?;
                } else {
                    item_dict.set_item(field.as_str(), py.None())?;
                }
            }
            
            py_list.append(item_dict)?;
        }
        
        Ok(py_list.into())
    }

    /// XPath selection - returns list of matching elements
    fn xpath(&self, xpath_expr: &str) -> PyResult<Vec<Element>> {
        let html_str = self.document.html();
        match parser::parse(&html_str) {
            Ok(package) => {
                let doc = package.as_document();
                match evaluate_xpath(&doc, xpath_expr) {
                    Ok(Value::Nodeset(nodeset)) => {
                        let mut elements = Vec::new();
                        for node in nodeset.iter() {
                            if let Node::Element(elem) = node {
                                // Convert sxd element to our Element type
                                let mut elem_html = format!("<{}", elem.name().local_part());
                                // Add attributes
                                for attr in elem.attributes() {
                                    elem_html.push_str(&format!(" {}=\"{}\"", attr.name().local_part(), attr.value()));
                                }
                                elem_html.push('>');
                                
                                // Add text content
                                let text_content = get_element_text(&elem);
                                elem_html.push_str(&text_content);
                                elem_html.push_str(&format!("</{}>", elem.name().local_part()));
                                
                                let parsed = Html::parse_fragment(&elem_html);
                                if let Some(element_ref) = parsed.select(&Selector::parse("*").unwrap()).next() {
                                    elements.push(Element::new(element_ref));
                                }
                            }
                        }
                        Ok(elements)
                    }
                    Ok(Value::String(s)) => {
                        // Return as text-only element
                        let elem_html = format!("<span>{}</span>", s);
                        let parsed = Html::parse_fragment(&elem_html);
                        if let Some(element_ref) = parsed.select(&Selector::parse("span").unwrap()).next() {
                            Ok(vec![Element::new(element_ref)])
                        } else {
                            Ok(vec![])
                        }
                    }
                    _ => Ok(vec![]),
                }
            }
            Err(_) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Failed to parse HTML for XPath"
            ))
        }
    }

    /// XPath selection - returns first matching element
    fn xpath_one(&self, xpath_expr: &str) -> PyResult<Option<Element>> {
        let results = self.xpath(xpath_expr)?;
        Ok(results.into_iter().next())
    }

    /// Get all matching XPath results as strings (Scrapy-compatible)
    fn xpath_getall(&self, xpath_expr: &str) -> PyResult<Vec<String>> {
        let html_str = self.document.html();
        match parser::parse(&html_str) {
            Ok(package) => {
                let doc = package.as_document();
                match evaluate_xpath(&doc, xpath_expr) {
                    Ok(Value::Nodeset(nodeset)) => {
                        let mut results = Vec::new();
                        for node in nodeset.iter() {
                            match node {
                                Node::Element(elem) => {
                                    results.push(get_element_text(&elem));
                                }
                                Node::Text(text) => {
                                    results.push(text.text().to_string());
                                }
                                Node::Attribute(attr) => {
                                    results.push(attr.value().to_string());
                                }
                                _ => {}
                            }
                        }
                        Ok(results)
                    }
                    Ok(Value::String(s)) => Ok(vec![s]),
                    Ok(Value::Number(n)) => Ok(vec![n.to_string()]),
                    Ok(Value::Boolean(b)) => Ok(vec![b.to_string()]),
                    _ => Ok(vec![]),
                }
            }
            Err(_) => Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Failed to parse HTML for XPath"
            ))
        }
    }

    /// Get first XPath result as string (Scrapy-compatible)
    fn xpath_get(&self, xpath_expr: &str) -> PyResult<Option<String>> {
        let results = self.xpath_getall(xpath_expr)?;
        Ok(results.into_iter().next())
    }
}

#[pyclass]
#[derive(Clone)]
pub struct Element {
    html: String,
    tag_name: String,
    attributes: HashMap<String, String>,
    text_content: String,
}

#[pymethods]
impl Element {
    /// Get the text content of the element
    fn text(&self) -> String {
        self.text_content.clone()
    }

    /// BeautifulSoup-like .get(attr, default=None)
    fn get(&self, py: Python, name: &str, default: Option<PyObject>) -> PyObject {
        if let Some(val) = self.attributes.get(name) {
            PyString::new_bound(py, val).into()
        } else {
            default.unwrap_or_else(|| py.None())
        }
    }

    /// Get an attribute value
    fn attr(&self, name: &str) -> Option<String> {
        self.attributes.get(name).cloned()
    }

    /// Get all attributes as a dict
    fn attrs(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new_bound(py);
        for (key, value) in &self.attributes {
            dict.set_item(key, value)?;
        }
        Ok(dict.into())
    }

    /// Get the tag name
    fn tag(&self) -> String {
        self.tag_name.clone()
    }

    /// Get the HTML of this element
    fn html(&self) -> String {
        self.html.clone()
    }

    /// Select within this element
    fn select(&self, selector: &str) -> PyResult<Vec<Element>> {
        let html = Html::parse_fragment(&self.html);
        let sel = get_or_compile_selector(selector)?;
        Ok(html.select(&sel)
            .map(|elem| Element::new(elem))
            .collect())
    }

    /// Select one within this element
    fn select_one(&self, selector: &str) -> PyResult<Option<Element>> {
        let html = Html::parse_fragment(&self.html);
        let sel = get_or_compile_selector(selector)?;
        Ok(html.select(&sel)
            .next()
            .map(|elem| Element::new(elem)))
    }

    /// Check if element has a class
    fn has_class(&self, class_name: &str) -> bool {
        self.attributes.get("class")
            .map(|classes| classes.split_whitespace().any(|c| c == class_name))
            .unwrap_or(false)
    }

    /// Get element id
    fn id(&self) -> Option<String> {
        self.attributes.get("id").cloned()
    }

    /// XPath selection within this element
    fn xpath(&self, xpath_expr: &str) -> PyResult<Vec<Element>> {
        match parser::parse(&self.html) {
            Ok(package) => {
                let doc = package.as_document();
                match evaluate_xpath(&doc, xpath_expr) {
                    Ok(Value::Nodeset(nodeset)) => {
                        let mut elements = Vec::new();
                        for node in nodeset.iter() {
                            if let Node::Element(elem) = node {
                                let mut elem_html = format!("<{}", elem.name().local_part());
                                for attr in elem.attributes() {
                                    elem_html.push_str(&format!(" {}=\"{}\"", attr.name().local_part(), attr.value()));
                                }
                                elem_html.push('>');
                                let text_content = get_element_text(&elem);
                                elem_html.push_str(&text_content);
                                elem_html.push_str(&format!("</{}>", elem.name().local_part()));
                                
                                let parsed = Html::parse_fragment(&elem_html);
                                if let Some(element_ref) = parsed.select(&Selector::parse("*").unwrap()).next() {
                                    elements.push(Element::new(element_ref));
                                }
                            }
                        }
                        Ok(elements)
                    }
                    _ => Ok(vec![]),
                }
            }
            Err(_) => Ok(vec![])
        }
    }

    /// XPath get all as strings (Scrapy-compatible)
    fn xpath_getall(&self, xpath_expr: &str) -> PyResult<Vec<String>> {
        match parser::parse(&self.html) {
            Ok(package) => {
                let doc = package.as_document();
                match evaluate_xpath(&doc, xpath_expr) {
                    Ok(Value::Nodeset(nodeset)) => {
                        let mut results = Vec::new();
                        for node in nodeset.iter() {
                            match node {
                                Node::Element(elem) => {
                                    results.push(get_element_text(&elem));
                                }
                                Node::Text(text) => {
                                    results.push(text.text().to_string());
                                }
                                Node::Attribute(attr) => {
                                    results.push(attr.value().to_string());
                                }
                                _ => {}
                            }
                        }
                        Ok(results)
                    }
                    Ok(Value::String(s)) => Ok(vec![s]),
                    Ok(Value::Number(n)) => Ok(vec![n.to_string()]),
                    Ok(Value::Boolean(b)) => Ok(vec![b.to_string()]),
                    _ => Ok(vec![]),
                }
            }
            Err(_) => Ok(vec![])
        }
    }

    /// XPath get first as string (Scrapy-compatible)
    fn xpath_get(&self, xpath_expr: &str) -> PyResult<Option<String>> {
        let results = self.xpath_getall(xpath_expr)?;
        Ok(results.into_iter().next())
    }

    fn __repr__(&self) -> String {
        format!("<Element '{}' {}>", self.tag_name, 
            if let Some(id) = self.id() {
                format!("id='{}'", id)
            } else if let Some(class) = self.attributes.get("class") {
                format!("class='{}'", class)
            } else {
                String::new()
            }
        )
    }

}

impl Element {
    fn new(elem: ElementRef) -> Self {
        let mut attributes = HashMap::new();
        for attr in elem.value().attrs() {
            attributes.insert(attr.0.to_string(), attr.1.to_string());
        }
        
        let text_content = elem.text()
            .collect::<Vec<_>>()
            .join(" ")
            .split_whitespace()
            .collect::<Vec<_>>()
            .join(" ");
        
        Element {
            html: elem.html(),
            tag_name: elem.value().name().to_string(),
            attributes,
            text_content,
        }
    }
}

fn get_or_compile_selector(selector: &str) -> PyResult<Selector> {
    let mut cache = SELECTOR_CACHE.lock().unwrap();
    
    if let Some(sel) = cache.get(selector) {
        return Ok(sel.clone());
    }
    
    match Selector::parse(selector) {
        Ok(sel) => {
            cache.insert(selector.to_string(), sel.clone());
            Ok(sel)
        }
        Err(_) => Err(PyErr::new::<crate::errors::SelectorError, _>(
            format!("Invalid CSS selector: {}", selector)
        ))
    }
}

fn get_element_text(elem: &sxd_document::dom::Element) -> String {
    let mut text = String::new();
    for child in elem.children() {
        match child {
            sxd_document::dom::ChildOfElement::Text(text_node) => {
                text.push_str(text_node.text());
            }
            sxd_document::dom::ChildOfElement::Element(child_elem) => {
                text.push_str(&get_element_text(&child_elem));
            }
            _ => {}
        }
    }
    text.trim().to_string()
}

/// Parse HTML and return a WebScraper instance
#[pyfunction]
pub fn parse_html(html: &str) -> WebScraper {
    WebScraper::new(html)
}

/// Parse HTML and extract data in one go
#[pyfunction]
pub fn extract(py: Python, html: &str, selectors: HashMap<String, String>) -> PyResult<PyObject> {
    let doc = Html::parse_document(html);
    let result = PyDict::new_bound(py);
    
    for (field, selector) in selectors {
        let sel = get_or_compile_selector(&selector)?;
        if let Some(elem) = doc.select(&sel).next() {
            let text = elem.text().collect::<Vec<_>>().join(" ").trim().to_string();
            result.set_item(field, text)?;
        } else {
            result.set_item(field, py.None())?;
        }
    }
    
    Ok(result.into())
}

/// Extract all matching elements' text
#[pyfunction]
pub fn extract_all(html: &str, selector: &str) -> PyResult<Vec<String>> {
    let doc = Html::parse_document(html);
    let sel = get_or_compile_selector(selector)?;
    
    Ok(doc.select(&sel)
        .map(|elem| elem.text().collect::<Vec<_>>().join(" ").trim().to_string())
        .filter(|s| !s.is_empty())
        .collect())
}