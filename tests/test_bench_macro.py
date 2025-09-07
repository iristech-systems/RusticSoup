import pytest

try:
    import rusticsoup
except Exception:
    rusticsoup = None


def ecommerce_grid(n=60):
    rows = []
    for i in range(n):
        rows.append(
            f"""
            <div class="product" data-id="{i}">
              <h2>Prod {i}</h2>
              <span class="price">${i}.99</span>
              <a class="buy" href="/buy/{i}">Buy</a>
              <img src="/img/{i}.jpg" alt="p{i}">
            </div>
            """
        )
    return "<div class='grid'>" + "".join(rows) + "</div>"


@pytest.mark.benchmark(group="macro_extract_bulk")
def test_extract_data_bulk_pages(benchmark):
    if rusticsoup is None:
        pytest.skip("rusticsoup not importable")

    pages = [ecommerce_grid(80) for _ in range(20)]
    mapping = {
        "title": "h2",
        "price": "span.price",
        "link": "a.buy@href",
        "image": "img@src",
    }

    def run():
        rusticsoup.extract_data_bulk(pages, "div.product", mapping)

    benchmark(run)


@pytest.mark.benchmark(group="macro_pipeline")
def test_parse_then_select_then_attr(benchmark):
    if rusticsoup is None:
        pytest.skip("rusticsoup not importable")

    html = ecommerce_grid(200)

    def run():
        doc = rusticsoup.parse_html(html)
        items = doc.select("div.product")
        # simulate attribute and text extraction
        res = []
        for it in items:
            title = it.select_one("h2").text()
            price = it.select_one(".price").text()
            link = it.select_one("a.buy").attr("href")
            res.append((title, price, link))
        return res

    benchmark(run)
