# Changelog

## 2026-01-19 - docs

- Add [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) and [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md).
- Link the new architecture and structure docs from [README.md](README.md).
- Add [docs/INSTALL.md](docs/INSTALL.md) and [docs/USAGE.md](docs/USAGE.md) stubs.
- Extend [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) with install and usage docs.
- Add unit test starter coverage for pgml_lint modules and plugin behaviors, with skips for IO-heavy scripts.
- Refresh [README.md](README.md) to point to install, usage, and core docs with a minimal quick start.

## 2026-01-18 - v26.01b1

Initial release as a standalone PyPI package.

- Remove leftover `pg_analyze` references from old repo structure.
- Update test imports: `pg_analyze.tokenize` -> `pgml_lint.parser`.
- Remove obsolete `test_pgml_blocks_sampler.py` that tested non-existent `pg_analyze.aggregate` module.

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
