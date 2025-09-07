def test_import():
    import rusticsoup  # noqa: F401


def test_api_surface_exists():
    import rusticsoup
    assert hasattr(rusticsoup, "extract_data")
    assert hasattr(rusticsoup, "extract_data_bulk")
    assert hasattr(rusticsoup, "parse_html")
