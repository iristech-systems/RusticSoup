use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use scraper::{Html, Selector};

enum ExtractionType {
    Text,
    Attribute(String),
    GetAll,
}

/// Universal HTML data extractor - works with any HTML structure
/// Just pass HTML + field mappings and get structured data back
#[pyfunction]
pub fn extract_data(
    py: Python,
    html: &str,
    container_selector: &str,
    field_mappings: &Bound<'_, PyDict>,
) -> PyResult<PyObject> {
    let document = Html::parse_document(html);
    let py_list = PyList::empty_bound(py);

    let container_sel = match Selector::parse(container_selector) {
        Ok(sel) => sel,
        Err(_) => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
            format!("Invalid container selector: {}", container_selector)
        )),
    };

    for container in document.select(&container_sel) {
        let item_dict = extract_item(py, &container, field_mappings)?;
        py_list.append(item_dict)?;
    }

    Ok(py_list.into())
}

fn extract_item(
    py: Python,
    container: &scraper::ElementRef,
    field_mappings: &Bound<'_, PyDict>,
) -> PyResult<Py<PyDict>> {
    let item_dict = PyDict::new_bound(py);
    let container_html = Html::parse_fragment(&container.html());

    for (field_name, selector_spec) in field_mappings.iter() {
        let field_name_str = field_name.extract::<String>()?;

        if let Ok(spec_str) = selector_spec.extract::<String>() {
            let (selector_str, extraction_type) = parse_selector_spec(&spec_str)
                .ok_or_else(|| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid selector spec: {}", spec_str)
                ))?;
            
            let selector = Selector::parse(&selector_str)
                .map_err(|_| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                    format!("Invalid selector '{}' for field '{}'", selector_str, field_name_str)
                ))?;

            match extraction_type {
                ExtractionType::Text => {
                    let value = container_html.select(&selector).next()
                        .map(|elem| elem.text().collect::<Vec<_>>().join(" ").trim().to_string())
                        .unwrap_or_default();
                    item_dict.set_item(field_name_str, value)?;
                },
                ExtractionType::Attribute(attr) => {
                    let value = container_html.select(&selector).next()
                        .and_then(|elem| elem.value().attr(&attr).map(ToString::to_string))
                        .unwrap_or_default();
                    item_dict.set_item(field_name_str, value)?;
                },
                ExtractionType::GetAll => {
                    let values = PyList::empty_bound(py);
                    for element in container_html.select(&selector) {
                        values.append(element.text().collect::<Vec<_>>().join(" ").trim().to_string())?;
                    }
                    item_dict.set_item(field_name_str, values)?;
                }
            }
        } else if let Ok(nested_mappings) = selector_spec.downcast::<PyDict>() {
            let nested_item = extract_item(py, container, nested_mappings)?;
            item_dict.set_item(field_name_str, nested_item)?;
        }
    }

    Ok(item_dict.into())
}

/// Parse selector specification (supports @attribute and @get_all syntax)
fn parse_selector_spec(spec: &str) -> Option<(String, ExtractionType)> {
    if spec.contains('@') {
        let parts: Vec<&str> = spec.splitn(2, '@').collect();
        if parts.len() == 2 {
            if parts[1] == "get_all" {
                Some((parts[0].to_string(), ExtractionType::GetAll))
            } else {
                Some((parts[0].to_string(), ExtractionType::Attribute(parts[1].to_string())))
            }
        } else {
            None
        }
    } else {
        Some((spec.to_string(), ExtractionType::Text))
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