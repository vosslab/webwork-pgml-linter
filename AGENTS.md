## Coding Style
See Python coding style in [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md).
See Markdown style in [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md).
See repo style in [docs/REPO_STYLE.md](docs/REPO_STYLE.md).
When making edits, document them in [docs/CHANGELOG.md](docs/CHANGELOG.md).
When in doubt, implement the changes the user asked for rather than waiting for a response; the user is not the best reader and will likely miss your request and then be confused why it was not implemented or fixed.
When changing code always run tests, documentation does not require tests.
Agents may run programs in the tests folder, including smoke tests and pyflakes/mypy runner scripts.

## Project Structure
This is a PyPI-packaged Python library. The main package is `pgml_lint/` at the repo root.
- `pgml_lint/` - Main package with lint engine, plugins, and rules
- `tools/` - Standalone command-line scripts
- `tests/` - Pytest test files
- `docs/` - Documentation

## Environment
Codex must run Python using `/opt/homebrew/opt/python@3.12/bin/python3.12` (use Python 3.12 only). This is only for Codex's runtime, not a requirement for repo scripts.
On this user's macOS (Homebrew Python 3.12), Python modules are installed to `/opt/homebrew/lib/python3.12/site-packages/`.

## Testing
Run tests with:
```bash
python3 -m pytest tests/
```
