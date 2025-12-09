"""
Type stubs for rusticsoup package.

This file provides IDE support for both Rust and Python components.
"""

from typing import Any, Dict, Type

# Re-export Rust components
from .rusticsoup import (
    Element,
    EncodingError,
    Field,
    HTMLParseError,
    PageObject,
    Processor,
    RusticSoup,
    RusticSoupError,
    SelectorError,
    WebPage,
    WebScraper,
    extract,
    extract_all,
    extract_data,
    extract_page_object,
    extract_table_data,
    extract_table_data,
    parse_html,
    processor,
    init_telemetry,
    shutdown_telemetry,
)

# Re-export Python helpers
from . import extractors, json_utils

# ItemPage type stub
class PageObjectMeta(type):
    """Metaclass that collects Field descriptors."""

    _fields: Dict[str, Field]

class ItemPage(metaclass=PageObjectMeta):
    """
    Base class for page objects with auto-extraction.

    When you define Field class attributes, ItemPage automatically extracts
    their values during __init__ and makes them available as instance attributes.

    Example:
        >>> class ProductPage(ItemPage):
        ...     title = Field(css="h1")
        ...     price = Field(css=".price")
        ...     offers = Field(container=".offer", mapping={'name': '.name'})
        ...
        >>> page = WebPage(html)
        >>> product = ProductPage(page)
        >>> print(product.title)  # Returns str, not Field!
        >>> print(len(product.offers))  # Returns list, not Field!
    """

    _page: WebPage
    _extracted: Dict[str, Any]

    def __init__(self, page: WebPage) -> None:
        """
        Initialize ItemPage and auto-extract all Field attributes.

        Args:
            page: WebPage to extract data from
        """
        ...

    def __getattribute__(self, name: str) -> Any:
        """
        Return extracted values for Field attributes.

        For Field attributes, returns the extracted value (str, list, dict, etc.)
        instead of the Field object itself.
        """
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Convert all extracted fields to a dictionary."""
        ...

class AutoExtract:
    """Decorator for auto-extracting page objects."""

    def __init__(self, page_class: Type[ItemPage]) -> None: ...
    def __call__(self, page: WebPage) -> ItemPage: ...

def page_object(cls: Type) -> Type[ItemPage]:
    """
    Decorator to convert a class into an ItemPage.

    Example:
        >>> @page_object
        ... class ProductPage:
        ...     title = Field(css="h1")
        ...     price = Field(css=".price")
    """
    ...

__all__ = [
    # Core classes (Rust)
    "Field",
    "WebPage",
    "Element",
    "WebScraper",
    "RusticSoup",
    "PageObject",
    "Processor",
    # Python helpers
    "ItemPage",
    "PageObjectMeta",
    "AutoExtract",
    "page_object",
    # Functions (Rust)
    "parse_html",
    "extract",
    "extract_all",
    "extract_data",
    "extract_page_object",
    "extract_table_data",
    "processor",
    # Exceptions (Rust)
    "RusticSoupError",
    "HTMLParseError",
    "SelectorError",
    "EncodingError",
    # Python modules
    "extractors",
    "json_utils",
    # Telemetry
    "init_telemetry",
    "shutdown_telemetry",
]

def init_telemetry(endpoint: str | None = None, headers: dict[str, str] | None = None, console: bool = False) -> None: ...
def shutdown_telemetry() -> None: ...

__version__: str
__doc__: str
