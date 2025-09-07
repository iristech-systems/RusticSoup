use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use rayon::prelude::*;
use std::collections::HashMap;

/// Parse multiple HTML pages in parallel and return structured results
#[pyfunction]
pub fn parse_multiple_google_pages(py: Python, html_pages: Vec<String>, page_identifiers: Vec<String>) -> PyResult<PyObject> {
    // Parallel processing of all pages at once
    let results: Vec<(String, Vec<PyObject>)> = html_pages
        .par_iter()
        .zip(page_identifiers.par_iter())
        .map(|(html, identifier)| {
            let ads = parse_google_page_internal(html);
            (identifier.clone(), ads)
        })
        .collect();
    
    // Convert to Python dict: {page_id: [ads]}
    let py_results = PyDict::new_bound(py);
    
    for (identifier, ads) in results {
        let py_ads_list = PyList::empty_bound(py);
        
        Python::with_gil(|py| -> PyResult<()> {
            for ad in ads {
                py_ads_list.append(ad)?;
            }
            Ok(())
        })?;
        
        py_results.set_item(identifier, py_ads_list)?;
    }
    
    Ok(py_results.into())
}

/// Ultra-fast bulk parsing of Google Shopping pages
#[pyfunction] 
pub fn bulk_parse_google_shopping(py: Python, html_pages: Vec<String>) -> PyResult<PyObject> {
    // Process all pages in parallel using Rayon
    let all_results: Vec<Vec<PyObject>> = html_pages
        .par_iter()
        .map(|html| parse_google_page_internal(html))
        .collect();
    
    // Convert to Python list of lists
    let py_results = PyList::empty_bound(py);
    
    for page_ads in all_results {
        let py_page_ads = PyList::empty_bound(py);
        
        Python::with_gil(|py| -> PyResult<()> {
            for ad in page_ads {
                py_page_ads.append(ad)?;
            }
            Ok(())
        })?;
        
        py_results.append(py_page_ads)?;
    }
    
    Ok(py_results.into())
}

/// Internal function to parse a single Google Shopping page
fn parse_google_page_internal(html: &str) -> Vec<PyObject> {
    Python::with_gil(|py| {
        let mut ads = Vec::new();
        
        // Parse HTML
        let document = scraper::Html::parse_document(html);
        
        // Check for container
        let container_selector = match scraper::Selector::parse("#sh-osd__online-sellers-cont") {
            Ok(sel) => sel,
            Err(_) => return ads,
        };
        
        if document.select(&container_selector).next().is_none() {
            return ads;
        }
        
        // Get all offer rows
        let row_selector = match scraper::Selector::parse(r#"tr[data-is-grid-offer="true"]"#) {
            Ok(sel) => sel,
            Err(_) => return ads,
        };
        
        // Parse each row
        for row in document.select(&row_selector) {
            if let Ok(ad) = parse_single_ad(py, row) {
                ads.push(ad);
            }
        }
        
        ads
    })
}

/// Parse a single ad row
fn parse_single_ad(py: Python, row: scraper::ElementRef) -> PyResult<PyObject> {
    // Extract seller name
    let seller_name = extract_seller_name(row);
    
    // Extract price
    let offer_price = extract_price(row);
    
    // Extract shipping
    let total_price = extract_shipping(row);
    
    // Extract link
    let link = extract_link(row);
    
    // Determine type
    let ad_type = if total_price.is_empty() { "Local" } else { "Online" };
    
    // Create Python dict
    let ad_dict = PyDict::new_bound(py);
    ad_dict.set_item("seller_name", seller_name)?;
    ad_dict.set_item("offer_price", offer_price)?;
    ad_dict.set_item("total_price", total_price)?;
    ad_dict.set_item("link", link)?;
    ad_dict.set_item("type", ad_type)?;
    
    Ok(ad_dict.into())
}

fn extract_seller_name(row: scraper::ElementRef) -> String {
    // Use the working selector: a.b5ycib
    let selector = match scraper::Selector::parse("a.b5ycib") {
        Ok(sel) => sel,
        Err(_) => return String::new(),
    };
    
    if let Some(seller_link) = row.select(&selector).next() {
        let text = seller_link.text().collect::<Vec<_>>().join("");
        text.replace("Opens in a new window", "").trim().to_string()
    } else {
        String::new()
    }
}

fn extract_price(row: scraper::ElementRef) -> String {
    let selector = match scraper::Selector::parse("span.g9WBQb") {
        Ok(sel) => sel,
        Err(_) => return String::new(),
    };
    
    if let Some(price_elem) = row.select(&selector).next() {
        price_elem.text().collect::<Vec<_>>().join("").trim().to_string()
    } else {
        String::new()
    }
}

fn extract_shipping(row: scraper::ElementRef) -> String {
    let selector = match scraper::Selector::parse("div.drzWO") {
        Ok(sel) => sel,
        Err(_) => return String::new(),
    };
    
    if let Some(shipping_elem) = row.select(&selector).next() {
        shipping_elem.text().collect::<Vec<_>>().join("").trim().to_string()
    } else {
        String::new()
    }
}

fn extract_link(row: scraper::ElementRef) -> String {
    let selector = match scraper::Selector::parse("a.UxuaJe") {
        Ok(sel) => sel,
        Err(_) => return String::new(),
    };
    
    if let Some(link_elem) = row.select(&selector).next() {
        if let Some(href) = link_elem.value().attr("href") {
            if href.starts_with("/url?q=") {
                format!("https://www.google.com{}", href)
            } else {
                href.to_string()
            }
        } else {
            String::new()
        }
    } else {
        String::new()
    }
}

/// Benchmark function to compare bulk vs individual parsing
#[pyfunction]
pub fn benchmark_bulk_parsing(py: Python, html_pages: Vec<String>, iterations: usize) -> PyResult<PyObject> {
    use std::time::Instant;
    
    // Benchmark individual parsing (Python loop)
    let start = Instant::now();
    for _ in 0..iterations {
        for html in &html_pages {
            let _ads = parse_google_page_internal(html);
        }
    }
    let individual_time = start.elapsed().as_secs_f64();
    
    // Benchmark bulk parsing (Rust parallel)
    let start = Instant::now();
    for _ in 0..iterations {
        let _all_results: Vec<Vec<PyObject>> = html_pages
            .par_iter()
            .map(|html| parse_google_page_internal(html))
            .collect();
    }
    let bulk_time = start.elapsed().as_secs_f64();
    
    // Return results
    let results = PyDict::new_bound(py);
    results.set_item("individual_time", individual_time)?;
    results.set_item("bulk_time", bulk_time)?;
    results.set_item("speedup", individual_time / bulk_time)?;
    results.set_item("pages_count", html_pages.len())?;
    results.set_item("iterations", iterations)?;
    
    Ok(results.into())
}