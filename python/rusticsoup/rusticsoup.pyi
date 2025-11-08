"""
Type stubs for rusticsoup Rust module.

This file provides IDE support and type hints for the Rust-compiled components.
"""

from typing import Any, Callable, Dict, List, Optional, Union

class Field:
    """
    Field descriptor for declarative data extraction with fallback selectors and list extraction.

    Defines how to extract data from a WebPage using CSS selectors. Supports:
    - Single or multiple fallback selectors
    - Container+mapping for extracting lists of structured data
    - Transformation pipelines

    Args:
        css: CSS selector(s) - string or list of strings for fallback (e.g., "h1.title" or ["h1.title", "h1"])
        xpath: XPath selector (not yet implemented)
        attr: Attribute to extract (e.g., "href", "src")
        get_all: If True, extract from all matching elements
        default: Default value if extraction fails
        required: If True, raise error if extraction fails
        transform: Function or list of functions to transform extracted value
        container: Container selector for list extraction (use with mapping)
        mapping: Field mappings dict for structured list extraction (use with container)

    Examples:
        >>> # Simple extraction
        >>> title = Field(css="h1")
        >>>
        >>> # Fallback selectors - tries each until one matches
        >>> price = Field(css=["span.price", "div.price", ".price"])
        >>>
        >>> # Extract attribute
        >>> link = Field(css="a.product", attr="href")
        >>>
        >>> # Extract all matching
        >>> tags = Field(css=".tag", get_all=True)
        >>>
        >>> # With transform
        >>> price = Field(css=".price", transform=lambda s: float(s.replace("$", "")))
        >>>
        >>> # List extraction with container+mapping
        >>> offers = Field(
        ...     container='div.offer',
        ...     mapping={
        ...         'title': 'h3',
        ...         'price': '.price',
        ...         'link': 'a@href'
        ...     }
        ... )
    """

    def __init__(
        self,
        *,
        css: Optional[Union[str, List[str]]] = None,
        xpath: Optional[str] = None,
        attr: Optional[str] = None,
        get_all: bool = False,
        default: Optional[str] = None,
        required: bool = True,
        transform: Optional[Union[Callable, List[Callable]]] = None,
        container: Optional[str] = None,
        mapping: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> None: ...
    def extract(self, page: WebPage) -> Any:
        """
        Extract value from WebPage based on field configuration.

        Args:
            page: WebPage instance to extract from

        Returns:
            Extracted value (type depends on configuration and transforms)

        Example:
            >>> page = WebPage(html)
            >>> field = Field(css="h1")
            >>> title = field.extract(page)
        """
        ...

class WebPage:
    """
    High-level HTML page abstraction with declarative extraction API.

    WebPage provides a clean, structured way to extract data from HTML documents,
    inspired by web-poet's Page objects.

    Args:
        html: HTML content as string
        url: Page URL (used for resolving relative URLs)
        metadata: Optional metadata dict

    Examples:
        >>> page = WebPage(html, url="https://example.com/product/123")
        >>> title = page.text("h1.title")
        >>> price = page.text(".price")
        >>> image = page.attr("img.product", "src")
    """

    def __init__(
        self,
        html: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None: ...
    def text(self, selector: str) -> str:
        """
        Extract text from first matching element.

        Args:
            selector: CSS selector

        Returns:
            Text content

        Example:
            >>> page.text("h1")
            'Product Title'
        """
        ...

    def text_all(self, selector: str) -> List[str]:
        """
        Extract text from all matching elements.

        Args:
            selector: CSS selector

        Returns:
            List of text content

        Example:
            >>> page.text_all(".tag")
            ['Python', 'Rust', 'Web']
        """
        ...

    def attr(self, selector: str, attribute: str) -> Optional[str]:
        """
        Extract attribute from first matching element.

        Args:
            selector: CSS selector
            attribute: Attribute name (e.g., "href", "src")

        Returns:
            Attribute value or None

        Example:
            >>> page.attr("a.product", "href")
            '/products/123'
        """
        ...

    def attr_all(self, selector: str, attribute: str) -> List[str]:
        """
        Extract attribute from all matching elements.

        Args:
            selector: CSS selector
            attribute: Attribute name

        Returns:
            List of attribute values

        Example:
            >>> page.attr_all("img", "src")
            ['/img1.jpg', '/img2.jpg']
        """
        ...

    def css(self, selector: str) -> str:
        """
        Get HTML of first matching element.

        Args:
            selector: CSS selector

        Returns:
            HTML string
        """
        ...

    def css_all(self, selector: str) -> List[str]:
        """
        Get HTML of all matching elements.

        Args:
            selector: CSS selector

        Returns:
            List of HTML strings
        """
        ...

    def has(self, selector: str) -> bool:
        """
        Check if element exists.

        Args:
            selector: CSS selector

        Returns:
            True if element exists

        Example:
            >>> if page.has(".out-of-stock"):
            ...     print("Out of stock!")
        """
        ...

    def count(self, selector: str) -> int:
        """
        Count matching elements.

        Args:
            selector: CSS selector

        Returns:
            Number of matching elements
        """
        ...

    def extract(self, field_mappings: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data using field mappings.

        Args:
            field_mappings: Dict mapping field names to selectors

        Returns:
            Dict of extracted data

        Example:
            >>> mappings = {
            ...     'title': 'h1',
            ...     'price': '.price',
            ...     'image': 'img@src'
            ... }
            >>> data = page.extract(mappings)
        """
        ...

    def extract_all(
        self, container_selector: str, field_mappings: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Extract multiple items using container and field mappings.

        Args:
            container_selector: CSS selector for item containers
            field_mappings: Dict mapping field names to selectors

        Returns:
            List of extracted items

        Example:
            >>> mappings = {'title': 'h2', 'price': '.price'}
            >>> products = page.extract_all('.product', mappings)
        """
        ...

    def absolute_url(self, url: str) -> str:
        """
        Convert relative URL to absolute using page's base URL.

        Args:
            url: Relative or absolute URL

        Returns:
            Absolute URL

        Example:
            >>> page = WebPage(html, url="https://example.com/page")
            >>> page.absolute_url("../image.jpg")
            'https://example.com/image.jpg'
        """
        ...

    def url(self) -> Optional[str]:
        """Get page URL."""
        ...

    def html(self) -> str:
        """Get raw HTML content."""
        ...

    def metadata(self) -> Dict[str, Any]:
        """Get page metadata."""
        ...

    def json_ld(self) -> List[Dict[str, Any]]:
        """
        Extract JSON-LD structured data.

        Returns:
            List of JSON-LD objects

        Example:
            >>> data = page.json_ld()
            >>> product_data = data[0]  # First JSON-LD object
        """
        ...

    def json_in_script(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Extract JSON from script tags.

        Args:
            pattern: Optional regex pattern to match specific JSON

        Returns:
            List of JSON objects found

        Example:
            >>> data = page.json_in_script()
            >>> # Or with pattern
            >>> data = page.json_in_script(r'window.data = ({.*?});')
        """
        ...

    def json_variable(self, variable_name: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON assigned to JavaScript variable.

        Args:
            variable_name: Name of JS variable

        Returns:
            JSON object or None

        Example:
            >>> data = page.json_variable('pageData')
        """
        ...

class Element:
    """
    Represents an HTML element with text and attribute access.

    Low-level element class for working with individual DOM nodes.
    """

    def text(self) -> str:
        """Get text content of element."""
        ...

    def html(self) -> str:
        """Get HTML content of element."""
        ...

    def attr(self, name: str) -> Optional[str]:
        """
        Get attribute value.

        Args:
            name: Attribute name

        Returns:
            Attribute value or None
        """
        ...

    def has_class(self, class_name: str) -> bool:
        """Check if element has CSS class."""
        ...

class WebScraper:
    """
    Low-level HTML parser for manual DOM traversal.

    Use WebPage for higher-level extraction. WebScraper is for
    advanced use cases requiring direct DOM manipulation.
    """

    def __init__(self, html: str) -> None: ...
    def select(self, selector: str) -> List[Element]:
        """Select all matching elements."""
        ...

    def select_one(self, selector: str) -> Optional[Element]:
        """Select first matching element."""
        ...

    def text(self) -> str:
        """Get all text from document."""
        ...

    def html(self) -> str:
        """Get HTML of document."""
        ...

    def links(self) -> List[str]:
        """Extract all links (href attributes)."""
        ...

    def images(self) -> List[str]:
        """Extract all image sources."""
        ...

class RusticSoup:
    """
    BeautifulSoup-like API for HTML parsing.

    Provides familiar BeautifulSoup methods for easy migration.
    """

    def __init__(self, html: str) -> None: ...
    def select(self, selector: str) -> List[Element]:
        """Select elements by CSS selector."""
        ...

    def select_one(self, selector: str) -> Optional[Element]:
        """Select first element by CSS selector."""
        ...

    def find_all(self, selector: str) -> List[Element]:
        """Alias for select()."""
        ...

    def find(self, selector: str) -> Optional[Element]:
        """Alias for select_one()."""
        ...

class PageObject:
    """Base class for PageObject pattern (advanced usage)."""

    def __init__(self, page: WebPage) -> None: ...

class Processor:
    """Function decorator for extraction processors (advanced usage)."""

    def __init__(self, func: Callable, input_type: Optional[str] = None) -> None: ...

# Exception classes
class RusticSoupError(Exception):
    """Base exception for RusticSoup errors."""

class HTMLParseError(RusticSoupError):
    """Raised when HTML parsing fails."""

class SelectorError(RusticSoupError):
    """Raised when CSS selector is invalid."""

class EncodingError(RusticSoupError):
    """Raised when character encoding detection fails."""

# Standalone functions
def parse_html(html: str) -> WebScraper:
    """
    Parse HTML into WebScraper instance.

    Args:
        html: HTML content

    Returns:
        WebScraper instance
    """
    ...

def extract_data(
    html: str, container_selector: str, field_mappings: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Extract data from HTML using container and field mappings.

    Args:
        html: HTML content
        container_selector: CSS selector for item containers
        field_mappings: Dict mapping field names to selectors/specs

    Returns:
        List of extracted items

    Example:
        >>> mappings = {
        ...     'title': 'h2',
        ...     'price': '.price',
        ...     'link': 'a@href',
        ...     'image': 'img@src',
        ... }
        >>> items = extract_data(html, '.product', mappings)
    """
    ...

def extract(
    html: str, selector: str, mappings: Dict[str, str]
) -> Optional[Dict[str, Any]]:
    """Extract single item."""
    ...

def extract_all(
    html: str, selector: str, mappings: Dict[str, str]
) -> List[Dict[str, Any]]:
    """Extract multiple items."""
    ...

def extract_table_data(html: str, table_selector: str) -> List[List[str]]:
    """
    Extract table data as 2D array.

    Args:
        html: HTML content
        table_selector: CSS selector for table

    Returns:
        List of rows, each row is list of cell values
    """
    ...

def extract_page_object(page: WebPage, page_object_class: type) -> Dict[str, Any]:
    """Extract PageObject fields (advanced usage)."""
    ...

def processor(input_type: Optional[str] = None) -> Processor:
    """Create processor decorator (advanced usage)."""
    ...

__version__: str
__doc__: str
__all__: List[str]
