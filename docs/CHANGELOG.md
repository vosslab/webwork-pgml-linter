# Changelog

## 2026-01-18 - v26.01b1

Initial release as a standalone PyPI package.

- Create `pgml_lint/` plugin framework with built-in PGML lint modules and tests.
- Add PGML-aware lint checks for blocks, heredocs, blanks, and inline markers.
- Add macro/assignment parsing with line-numbered output and optional JSON summaries.
- Fix MathObjects false positive: recognize that `PGML.pl` loads `MathObjects.pl` internally.
- Add math span masking (`[`...`]` and `[:...:+]`) to bracket checker to avoid false positives from LaTeX interval notation.
- Disable `pgml_brackets` plugin by default since plain brackets in PGML text are common.
- Add array/hash variable detection to assignment checker: recognize `@arr =` and `%hash =` patterns.
- Simplify lint CLI: just `-i`/`-d` for input, `-v`/`-q` for verbosity.
- Add comprehensive PGML lint documentation:
  - [docs/PGML_LINT.md](docs/PGML_LINT.md): Usage guide and quick start
  - [docs/PGML_LINT_CONCEPTS.md](docs/PGML_LINT_CONCEPTS.md): PGML syntax concepts the linter validates
  - [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md): Reference for all built-in plugins
  - [docs/PGML_LINT_PLUGIN_DEV.md](docs/PGML_LINT_PLUGIN_DEV.md): Guide for writing custom plugins
  - [docs/PGML_LINT_ARCHITECTURE.md](docs/PGML_LINT_ARCHITECTURE.md): Internal architecture for contributors
