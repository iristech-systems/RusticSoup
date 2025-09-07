use pyo3::create_exception;
use pyo3::exceptions::PyException;

// Define Python-visible exception classes. For now, they all inherit from PyException.
// We can later make them share a common base if needed.
create_exception!(rusticsoup, RusticSoupError, PyException);
create_exception!(rusticsoup, HTMLParseError, RusticSoupError);
create_exception!(rusticsoup, SelectorError, RusticSoupError);
create_exception!(rusticsoup, EncodingError, RusticSoupError);
