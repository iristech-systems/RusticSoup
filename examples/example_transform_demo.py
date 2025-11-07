"""
Complete demonstration of Field transform feature in RusticSoup v0.2.2
"""

from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage
from datetime import datetime


# Example HTML
html = """
<html>
<body>
    <article>
        <h1>  understanding rust and python integration  </h1>
        <div class="author">by JOHN DOE</div>
        <time datetime="2025-01-07">January 7, 2025</time>
        <div class="price">Price: $1,234.56</div>
        <div class="content">
            <p>First paragraph about Rust.</p>
            <p>Second paragraph about Python.</p>
            <p>Third paragraph about integration.</p>
        </div>
        <span class="tag">rust</span>
        <span class="tag">python</span>
        <span class="tag">programming</span>
        <a href="/product/123">Buy Now</a>
    </article>
</body>
</html>
"""


# Define transform functions
def clean_author(text):
    """Remove 'by' prefix and title case"""
    return text.replace("by ", "").title()


def format_date(date_str):
    """Format ISO date to readable format"""
    dt = datetime.fromisoformat(date_str)
    return dt.strftime("%B %d, %Y")


def extract_price(text):
    """Extract numeric price from text"""
    import re

    match = re.search(r"\$([0-9,]+\.[0-9]{2})", text)
    return match.group(1) if match else "0.00"


def join_paragraphs(paragraphs):
    """Join paragraphs with double newline"""
    return "\n\n".join(paragraphs)


def make_absolute_url(relative_url):
    """Convert relative URL to absolute"""
    return f"https://example.com{relative_url}"


# Define Article page object with transforms
class Article(ItemPage):
    # Title: strip whitespace and title case
    title = Field(css="h1", transform=[str.strip, str.title])

    # Author: clean and format
    author = Field(css=".author", transform=clean_author)

    # Date: format from datetime attribute
    date = Field(css="time", attr="datetime", transform=format_date)

    # Price: extract and convert to float
    price = Field(
        css=".price", transform=[extract_price, lambda s: s.replace(",", ""), float]
    )

    # Content: join all paragraphs
    content = Field(css=".content p", get_all=True, transform=join_paragraphs)

    # Tags: uppercase all tags
    tags = Field(
        css=".tag", get_all=True, transform=lambda tags: [t.upper() for t in tags]
    )

    # URL: make absolute
    url = Field(css="a", attr="href", transform=make_absolute_url)


def main():
    print("=" * 60)
    print("RusticSoup v0.2.2 - Field Transform Demo")
    print("=" * 60)
    print()

    # Create WebPage and extract
    page = WebPage(html, url="https://example.com")
    article = Article(page)

    # Display results
    print("📄 Extracted Article Data:")
    print("-" * 60)
    print(f"Title:   {article.title}")
    print(f"Author:  {article.author}")
    print(f"Date:    {article.date}")
    print(f"Price:   ${article.price:.2f}")
    print(f"Tags:    {', '.join(article.tags)}")
    print(f"URL:     {article.url}")
    print()
    print("Content:")
    print("-" * 60)
    print(article.content)
    print()

    # Show dictionary representation
    print("📋 Dictionary Representation:")
    print("-" * 60)
    import json

    print(json.dumps(article.to_dict(), indent=2))
    print()

    print("=" * 60)
    print("✅ All transforms applied successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
