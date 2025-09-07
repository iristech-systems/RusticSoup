use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use scraper::{Html, Selector};
use std::collections::HashMap;

/// Universal HTML data extractor - works with any HTML structure
/// Just pass HTML + field mappings and get structured data back
#[pyfunction]
pub fn extract_data(
    py: Python,
    html: &str,
    container_selector: &str,
    field_mappings: HashMap<String, String>
) -> PyResult<PyObject> {
    let document = Html::parse_document(html);
    let py_list = PyList::empty_bound(py);
    
    // Parse container selector
    let container_sel = match Selector::parse(container_selector) {
        Ok(sel) => sel,
        Err(_) => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid container selector: {}", container_selector)
        ))
    };
    
    // Pre-compile all field selectors
    let mut compiled_selectors = HashMap::new();
    for (field_name, selector_spec) in &field_mappings {
        if let Some((selector_str, attr_name)) = parse_selector_spec(selector_spec) {
            let selector = match Selector::parse(&selector_str) {
                Ok(sel) => sel,
                Err(_) => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid selector '{}' for field '{}'", selector_str, field_name)
                ))
            };
            compiled_selectors.insert(field_name.clone(), (selector, attr_name));
        }
    }
    
    // Extract data from each container
    for container in document.select(&container_sel) {
        let item_dict = PyDict::new_bound(py);
        let container_html = Html::parse_fragment(&container.html());
        
        for (field_name, (selector, attr_name)) in &compiled_selectors {
            let value = if let Some(element) = container_html.select(selector).next() {
                if let Some(attr) = attr_name {
                    // Extract attribute
                    element.value().attr(attr).unwrap_or("").to_string()
                } else {
                    // Extract text content
                    element.text().collect::<Vec<_>>().join(" ").trim().to_string()
                }
            } else {
                String::new()
            };
            
            item_dict.set_item(field_name.as_str(), value)?;
        }
        
        py_list.append(item_dict)?;
    }
    
    Ok(py_list.into())
}

/// Universal bulk extractor - process multiple HTML pages at once
#[pyfunction]
pub fn extract_data_bulk(
    py: Python,
    html_pages: Vec<String>,
    container_selector: &str,
    field_mappings: HashMap<String, String>
) -> PyResult<PyObject> {
    use rayon::prelude::*;
    
    // Process all pages in parallel
    let results: Vec<Vec<HashMap<String, String>>> = html_pages
        .par_iter()
        .map(|html| extract_single_page(html, container_selector, &field_mappings))
        .collect();
    
    // Convert to Python
    let py_list = PyList::empty_bound(py);
    for page_results in results {
        let page_list = PyList::empty_bound(py);
        for item in page_results {
            let item_dict = PyDict::new_bound(py);
            for (key, value) in item {
                item_dict.set_item(key, value)?;
            }
            page_list.append(item_dict)?;
        }
        py_list.append(page_list)?;
    }
    
    Ok(py_list.into())
}

/// Extract data from a single page (internal function)
fn extract_single_page(
    html: &str,
    container_selector: &str,
    field_mappings: &HashMap<String, String>
) -> Vec<HashMap<String, String>> {
    let document = Html::parse_document(html);
    let mut results = Vec::new();
    
    // Parse selectors
    let container_sel = match Selector::parse(container_selector) {
        Ok(sel) => sel,
        Err(_) => return results,
    };
    
    let mut compiled_selectors = HashMap::new();
    for (field_name, selector_spec) in field_mappings {
        if let Some((selector_str, attr_name)) = parse_selector_spec(selector_spec) {
            if let Ok(selector) = Selector::parse(&selector_str) {
                compiled_selectors.insert(field_name.clone(), (selector, attr_name));
            }
        }
    }
    
    // Extract data
    for container in document.select(&container_sel) {
        let mut item = HashMap::new();
        let container_html = Html::parse_fragment(&container.html());
        
        for (field_name, (selector, attr_name)) in &compiled_selectors {
            let value = if let Some(element) = container_html.select(selector).next() {
                if let Some(attr) = attr_name {
                    element.value().attr(attr).unwrap_or("").to_string()
                } else {
                    element.text().collect::<Vec<_>>().join(" ").trim().to_string()
                }
            } else {
                String::new()
            };
            
            item.insert(field_name.clone(), value);
        }
        
        results.push(item);
    }
    
    results
}

/// Parse selector specification (supports @attribute syntax)
fn parse_selector_spec(spec: &str) -> Option<(String, Option<String>)> {
    if spec.contains('@') {
        let parts: Vec<&str> = spec.split('@').collect();
        if parts.len() == 2 {
            Some((parts[0].to_string(), Some(parts[1].to_string())))
        } else {
            None
        }
    } else {
        Some((spec.to_string(), None))
    }
}

/// Generic table data extractor - works with any table structure
#[pyfunction]
pub fn extract_table_data(py: Python, html: &str, table_selector: &str) -> PyResult<PyObject> {
    let document = Html::parse_document(html);
    let py_list = PyList::empty_bound(py);
    
    let table_sel = match Selector::parse(table_selector) {
        Ok(sel) => sel,
        Err(_) => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid table selector: {}", table_selector)
        ))
    };
    
    let row_sel = Selector::parse("tr").unwrap();
    let cell_sel = Selector::parse("td, th").unwrap();
    
    for table in document.select(&table_sel) {
        let table_html = Html::parse_fragment(&table.html());
        
        for row in table_html.select(&row_sel) {
            let row_data = PyList::empty_bound(py);
            
            for cell in row.select(&cell_sel) {
                let cell_text = cell.text().collect::<Vec<_>>().join(" ").trim().to_string();
                row_data.append(cell_text)?;
            }
            
            if row_data.len() > 0 {
                py_list.append(row_data)?;
            }
        }
    }
    
    Ok(py_list.into())
}