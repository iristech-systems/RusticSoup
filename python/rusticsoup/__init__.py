"""
RusticSoup - Lightning-fast HTML parser and data extractor

This module combines Rust-based high-performance HTML parsing with Python-based
helper classes for the PageObject pattern.
"""

# Import all Rust exports
from .rusticsoup import *  # noqa: F403

# Import specific items we need for type hints and runtime checks
from .rusticsoup import Field, WebPage  # noqa: F401

# Import the rust module itself to access metadata
from . import rusticsoup as _rusticsoup_module

# Import version and metadata from Rust module
__doc__ = _rusticsoup_module.__doc__
__version__ = _rusticsoup_module.__version__


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


# Update __all__ to include helper classes
__all__ = list(
    _rusticsoup_module.__all__ if hasattr(_rusticsoup_module, "__all__") else []
) + [
    "ItemPage",
    "AutoExtract",
    "page_object",
    "PageObjectMeta",
]
