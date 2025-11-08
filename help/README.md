# RusticSoup Help Center

Welcome to the RusticSoup documentation hub. This directory collects guides, APIs, and patterns with lots of examples to help you build fast, declarative scrapers that can compete with BeautifulSoup (BS4) both in speed and developer experience.

- If you are new, start with Quickstart, then read the WebPage API.
- Prefer declarative, reusable scraping? Check out Field and the PageObject pattern.
- Looking for lots of examples? See the Examples section and the test suite links.

## Table of Contents

- Quick Start
  - WebPage API Quick Start: ./quickstart.md
- Core API
  - WebPage API Reference: ./webpage_api.md
  - Field Usage Guide: ./field_usage.md
  - Field Transform Guide: ./field_transform.md
  - Containers & Mappings Guide: ./containers_and_mappings.md
  - Fallback Selectors Guide: ./fallback_selectors.md
  - ItemPage Containers + Mapping: ./itempage_containers.md
  - PageObject Pattern: ./page_object_pattern.md
- Examples
  - Examples directory (ready-to-run): ../../examples
  - More example-driven docs: ../benchmarks.md
  - Test suites as executable examples:
    - test_webpage_api.py
    - test_field_usage.py
    - tests/test_field_transform.py
    - test_page_object_pattern.py
    - test_itempage_field.py
    - test_new_features.py

## How this documentation is organized

- Each guide is self-contained and packed with copy-pasteable snippets.
- All examples favor the high-level WebPage API and the PageObject pattern.
- Whenever helpful, we show both “direct WebPage” and “Field/PageObject” ways to do the same task.

## Next steps

- Read Quick Start to get productive in minutes: ./quickstart.md
- Browse the API reference for everything WebPage can do: ./webpage_api.md
- Build reusable extractors with Field and the PageObject pattern:
  - ./field_usage.md
  - ./field_transform.md
  - ./page_object_pattern.md

---

Built with 🦀 by the RusticSoup team
