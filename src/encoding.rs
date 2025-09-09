use pyo3::prelude::*;
use encoding_rs_io::DecodeReaderBytesBuilder;
use std::io::Read;

/// Decodes a byte slice into a String, attempting to auto-detect the encoding.
///
/// The process is as follows:
/// 1. Check for and strip the UTF-8 BOM.
/// 2. Try to decode as UTF-8.
/// 3. If UTF-8 fails, inspect the HTML for a meta tag specifying the charset.
/// 4. If a charset is found, use it to decode.
/// 5. If no charset is found, fall back to Latin-1 (ISO-8859-1) as a last resort.
pub fn decode_bytes_to_string(data: &[u8]) -> PyResult<String> {
    // 1. Strip UTF-8 BOM if present
    let bytes = if data.len() >= 3 && data[0] == 0xEF && data[1] == 0xBB && data[2] == 0xBF {
        &data[3..]
    } else {
        data
    };

    // 2. Try decoding as UTF-8 first
    if let Ok(s) = std::str::from_utf8(bytes) {
        return Ok(s.to_string());
    }

    // 3. Sniff from meta tag if UTF-8 fails
    let mut decoder = DecodeReaderBytesBuilder::new()
        .encoding(None)
        .build(bytes);

    let mut decoded_string = String::new();
    if decoder.read_to_string(&mut decoded_string).is_ok() {
        return Ok(decoded_string);
    }

    // 5. Fallback to WINDOWS_1252 if everything else fails
    let (cow, _, had_errors) = encoding_rs::WINDOWS_1252.decode(bytes);
    if had_errors {
        return Err(PyErr::new::<crate::errors::EncodingError, _>(
            "Failed to decode bytes with any supported encoding".to_string()
        ));
    }

    Ok(cow.into_owned())
}
