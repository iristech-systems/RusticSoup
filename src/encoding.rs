use pyo3::prelude::*;

/// Minimal UTF-8 (with optional BOM) decoder to bootstrap encoding support.
/// - If data starts with UTF-8 BOM (0xEF,0xBB,0xBF), strip it.
/// - Attempt UTF-8 decode; on failure, raise EncodingError.
pub fn decode_bytes_to_string(data: &[u8]) -> PyResult<String> {
    let bytes = if data.len() >= 3 && data[0] == 0xEF && data[1] == 0xBB && data[2] == 0xBF {
        &data[3..]
    } else {
        data
    };
    match std::str::from_utf8(bytes) {
        Ok(s) => Ok(s.to_string()),
        Err(e) => Err(PyErr::new::<crate::errors::EncodingError, _>(
            format!("Failed to decode bytes as UTF-8: {}", e)
        )),
    }
}
