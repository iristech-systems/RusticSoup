import pytest

try:
    import rusticsoup
except Exception as e:  # pragma: no cover - import failure should fail tests
    rusticsoup = None


def small_html():
    return (
        "<div class='wrap'>"
        "<ul>"
        + "".join(
            f"<li class='item'><a href='/p/{i}'><span class='price'>$ {i}.99</span></a></li>"
            for i in range(10)
        )
        + "</ul>" "</div>"
    )


def medium_html(n=200):
    # generate n items
    items = "".join(
        f"<div class='card' data-i='{i}'>"
        f"<h2>Title {i}</h2>"
        f"<a class='buy' href='/buy/{i}'>buy</a>"
        f"<img src='/img/{i}.jpg' alt='p{i}'/>"
        f"<span class='price'>{i}.00</span>"
        f"</div>"
        for i in range(n)
    )
    return f"<section class='grid'>{items}</section>"


@pytest.mark.benchmark(group="parse_html")
def test_parse_small_html(benchmark):
    if rusticsoup is None:
        pytest.skip("rusticsoup not importable")

    html = small_html()

    def run():
        rusticsoup.parse_html(html)

    benchmark(run)


@pytest.mark.benchmark(group="extract_data")
def test_extract_data_small(benchmark):
    if rusticsoup is None:
        pytest.skip("rusticsoup not importable")

    html = small_html()
    mapping = {"price": "span.price", "link": "a@href"}

    def run():
        rusticsoup.extract_data(html, "li.item", mapping)

    benchmark(run)


@pytest.mark.benchmark(group="select")
def test_select_many_medium(benchmark):
    if rusticsoup is None:
        pytest.skip("rusticsoup not importable")

    html = medium_html(500)
    doc = rusticsoup.parse_html(html)

    def run():
        # Selecting multiple times to exercise selector engine
        for _ in range(5):
            doc.select("div.card .price")

    benchmark(run)
