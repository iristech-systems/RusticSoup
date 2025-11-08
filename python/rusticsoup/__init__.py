"""
RusticSoup - Lightning-fast HTML parser and data extractor

This module combines Rust-based high-performance HTML parsing with Python-based
helper classes for the PageObject pattern.
"""

# Import the Rust module
from . import rusticsoup as _rusticsoup

# Re-export everything from the Rust module
from .rusticsoup import (  # noqa: F401
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
    parse_html,
    processor,
)

# Import version and metadata from Rust module
__doc__ = _rusticsoup.__doc__
__version__ = _rusticsoup.__version__

# Import utility modules
from . import extractors
from . import json_utils

# Convenience imports for common extractors
from .extractors import (
    extract_price,
    extract_int,
    extract_bool,
    extract_email,
    extract_phone,
    extract_url,
    clean_text,
)
from .json_utils import (
    extract_json_ld,
    extract_json_from_script,
    extract_json_variable,
)


# Python-side helper classes for PageObject pattern
class PageObjectMeta(type):
    """Metaclass that collects Field descriptors from class definition"""

    def __new__(mcs, name, bases, namespace):
        # Collect all Field descriptors
        fields = {}
        for key, value in namespace.items():
            if isinstance(value, Field):
                fields[key] = value

        # Store fields on the class
        namespace["_fields"] = fields

        return super().__new__(mcs, name, bases, namespace)


class ItemPage(metaclass=PageObjectMeta):
    """
    Base class for page objects that auto-extract fields.

    Usage:
        class ProductPage(ItemPage):
            title = Field(css="h1.product-title")
            price = Field(css=".price")
            images = Field(css="img.product", attr="src", get_all=True)

        # Auto-extract on instantiation
        page = WebPage(html)
        product = ProductPage(page)
        print(product.title)   # Auto-extracted!
        print(product.price)   # Auto-extracted!
    """

    def __init__(self, page: WebPage):
        """
        Initialize page object and auto-extract all fields.

        Args:
            page: WebPage instance to extract from
        """
        self._page = page
        self._extracted = {}

        # Get fields from class (not instance)
        fields = getattr(self.__class__, "_fields", {})

        # Auto-extract all fields
        for field_name, field in fields.items():
            self._extracted[field_name] = field.extract(page)

    def __getattribute__(self, name):
        """Override to return extracted values instead of Field objects"""
        # Allow access to special attributes
        if name.startswith("_") or name in ("to_dict",):
            return object.__getattribute__(self, name)

        # Check if it's an extracted field
        try:
            extracted = object.__getattribute__(self, "_extracted")
            if name in extracted:
                return extracted[name]
        except AttributeError:
            pass

        # Fall back to normal attribute access
        return object.__getattribute__(self, name)

    def to_dict(self):
        """Convert to dictionary"""
        return dict(self._extracted)

    def __repr__(self):
        class_name = self.__class__.__name__
        fields = ", ".join(f"{k}={repr(v)[:50]}" for k, v in self._extracted.items())
        return f"{class_name}({fields})"


class AutoExtract:
    """
    Decorator that makes a class auto-extract from a page.

    Usage:
        @AutoExtract
        class Article:
            title = Field(css="h1")
            author = Field(css=".author")
            tags = Field(css=".tag", get_all=True)

        # Auto-extract
        page = WebPage(html)
        article = Article(page)
        print(article.title)
    """

    def __init__(self, cls):
        self.cls = cls
        self._fields = {}

        # Collect fields from class
        for key, value in vars(cls).items():
            if isinstance(value, Field):
                self._fields[key] = value

    def __call__(self, page: WebPage):
        """Create instance with auto-extracted fields"""
        instance = object.__new__(self.cls)
        instance._page = page
        instance._extracted = {}

        # Extract all fields
        for field_name, field in self._fields.items():
            instance._extracted[field_name] = field.extract(page)

        return instance

    def __getattr__(self, name):
        return getattr(self.cls, name)


def page_object(cls):
    """
    Class decorator for creating page objects with auto-extraction.

    Usage:
        @page_object
        class Product:
            title = Field(css="h1.title")
            price = Field(css=".price")
            rating = Field(css=".rating")

        page = WebPage(html)
        product = Product(page)
        print(product.title)   # Auto-extracted!
    """

    class PageObjectWrapper:
        def __init__(self, page: WebPage):
            self._page = page
            self._extracted = {}

            # Extract all Field attributes from the class
            for key in dir(cls):
                if not key.startswith("_"):
                    attr = getattr(cls, key)
                    if isinstance(attr, Field):
                        self._extracted[key] = attr.extract(page)

        def __getattr__(self, name):
            if name in self._extracted:
                return self._extracted[name]
            raise AttributeError(f"'{cls.__name__}' has no attribute '{name}'")

        def to_dict(self):
            return dict(self._extracted)

        def __repr__(self):
            fields = ", ".join(
                f"{k}={repr(v)[:50]}" for k, v in self._extracted.items()
            )
            return f"{cls.__name__}({fields})"

    PageObjectWrapper.__name__ = cls.__name__
    PageObjectWrapper.__qualname__ = cls.__qualname__

    return PageObjectWrapper


# Extend WebPage with JSON extraction methods
def _webpage_json_ld(self):
    """
    Extract JSON-LD structured data from the page.

    Returns:
        List of JSON-LD objects

    Example:
        >>> page = WebPage(html)
        >>> data = page.json_ld()
        >>> print(data[0]['@type'])
    """
    return extract_json_ld(self.html())


def _webpage_json_in_script(self, pattern=None):
    """
    Extract JSON objects from script tags.

    Args:
        pattern: Optional regex pattern to match specific JSON

    Returns:
        List of JSON objects

    Example:
        >>> page = WebPage(html)
        >>> data = page.json_in_script()
    """
    return extract_json_from_script(self.html(), pattern)


def _webpage_json_variable(self, variable_name):
    """
    Extract JSON assigned to a JavaScript variable.

    Args:
        variable_name: Name of the JS variable

    Returns:
        JSON object or None

    Example:
        >>> page = WebPage(html)
        >>> data = page.json_variable('pageData')
    """
    return extract_json_variable(self.html(), variable_name)


# Monkey-patch WebPage with new methods
WebPage.json_ld = _webpage_json_ld
WebPage.json_in_script = _webpage_json_in_script
WebPage.json_variable = _webpage_json_variable


# Build __all__ with Rust exports and Python helpers
__all__ = [
    # Rust exports
    "Element",
    "EncodingError",
    "Field",
    "HTMLParseError",
    "PageObject",
    "Processor",
    "RusticSoup",
    "RusticSoupError",
    "SelectorError",
    "WebPage",
    "WebScraper",
    "extract",
    "extract_all",
    "extract_data",
    "extract_page_object",
    "extract_table_data",
    "parse_html",
    "processor",
    # Python helper classes
    "ItemPage",
    "AutoExtract",
    "page_object",
    "PageObjectMeta",
    # Utility modules
    "extractors",
    "json_utils",
    # Common extractors
    "extract_price",
    "extract_int",
    "extract_bool",
    "extract_email",
    "extract_phone",
    "extract_url",
    "clean_text",
    # JSON utilities
    "extract_json_ld",
    "extract_json_from_script",
    "extract_json_variable",
]
