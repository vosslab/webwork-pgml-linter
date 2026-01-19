# File structure

## Top-level layout

- [AGENTS.md](AGENTS.md) lists agent workflow, style, environment, and testing expectations.
- [README.md](README.md) provides a user-facing overview, install steps, and quick start.
- [LICENSE](LICENSE) contains the LGPL license text.
- [VERSION](VERSION) stores the repo version.
- [MANIFEST.in](MANIFEST.in) defines source distribution contents.
- [pyproject.toml](pyproject.toml) defines package metadata, dependencies, and entry points.
- [pip_requirements.txt](pip_requirements.txt) lists development dependencies.
- [pgml_lint/](pgml_lint/) contains the library source code and built-in plugins.
- [tools/](tools/) contains CLI scripts.
- [tests/](tests/) contains pytest suites and lint checks.
- [docs/](docs/) contains project documentation.
- [devel/](devel/) holds release helper scripts.

## Key subtrees

- [pgml_lint/](pgml_lint/) houses the parser, engine, rules, registry, and plugin modules.
- [pgml_lint/plugins/](pgml_lint/plugins/) contains built-in lint checks registered by the plugin registry.
- [tests/](tests/) includes PGML lint tests plus ASCII compliance, pyflakes, indentation, and shebang checks.
- [tools/](tools/) currently provides the [tools/webwork_pgml_simple_lint.py](tools/webwork_pgml_simple_lint.py) CLI wrapper.
- [docs/](docs/) includes usage and architecture docs such as [docs/PGML_LINT.md](docs/PGML_LINT.md) and [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md).

## Generated artifacts

- No .gitignore file is present to document ignored or generated artifacts.

## Documentation map

- Root docs: [README.md](README.md) and [AGENTS.md](AGENTS.md).
- Style guides: [docs/MARKDOWN_STYLE.md](docs/MARKDOWN_STYLE.md), [docs/PYTHON_STYLE.md](docs/PYTHON_STYLE.md), [docs/REPO_STYLE.md](docs/REPO_STYLE.md).
- Setup and usage: [docs/INSTALL.md](docs/INSTALL.md) and [docs/USAGE.md](docs/USAGE.md).
- Linter docs: [docs/PGML_LINT.md](docs/PGML_LINT.md), [docs/PGML_LINT_CONCEPTS.md](docs/PGML_LINT_CONCEPTS.md), [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md), [docs/PGML_LINT_PLUGIN_DEV.md](docs/PGML_LINT_PLUGIN_DEV.md), [docs/PGML_LINT_ARCHITECTURE.md](docs/PGML_LINT_ARCHITECTURE.md).
- Architecture and structure: [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) and [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md).

## Where to add new work

- Core lint logic belongs in [pgml_lint/](pgml_lint/) and new plugins go under [pgml_lint/plugins/](pgml_lint/plugins/).
- Rule defaults live in [pgml_lint/rules.py](pgml_lint/rules.py); custom rule files should be consumed by callers that pass a JSON rules path.
- CLI scripts belong in [tools/](tools/).
- Tests belong in [tests/](tests/) with names like test_*.py.
- Documentation belongs in [docs/](docs/) using SCREAMING_SNAKE_CASE filenames.
