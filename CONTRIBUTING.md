### Contributing to rusticsoup

Thanks for considering a contribution!

#### Quick start
1. Install prerequisites: Python 3.11+, Rust stable, maturin.
2. Create venv and install dev deps:
   - pip install -e .[dev]
   - pre-commit install
3. Build locally:
   - maturin develop --release
4. Run tests:
   - pytest -q

#### Coding standards
- Python: ruff + black via pre-commit.
- Rust: rustfmt + clippy; keep unsafe minimal and documented.

#### Pull requests
- Include tests for new behavior.
- Update README/docs as needed.
- Use Conventional Commits in the PR title (e.g., feat:, fix:, chore:, docs:).

#### Release
- Maintainers publish by tagging vX.Y.Z; CI will publish to PyPI.
