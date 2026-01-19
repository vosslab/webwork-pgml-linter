# Code architecture

## Overview

This project provides a static linter for WeBWorK .pg files with a PGML-focused pipeline that parses file text, builds a shared lint context, runs plugins, and reports issues.

## Major components

- [pgml_lint/parser.py](pgml_lint/parser.py) strips comments and heredocs, tracks line positions, extracts PGML regions, and detects macro and variable usage.
- [pgml_lint/engine.py](pgml_lint/engine.py) builds the shared context and runs enabled plugins, returning a sorted issue list.
- [pgml_lint/rules.py](pgml_lint/rules.py) defines default block and macro rules and loads optional rule overrides from JSON.
- [pgml_lint/registry.py](pgml_lint/registry.py) and [pgml_lint/plugins/](pgml_lint/plugins/) manage built-in plugins and plugin registration.
- [pgml_lint/core.py](pgml_lint/core.py) formats issues and summarizes error and warning counts.
- [tools/webwork_pgml_simple_lint.py](tools/webwork_pgml_simple_lint.py) provides a CLI that scans .pg files and prints or serializes lint output.

## Data flow

- The CLI loads rule sets from [pgml_lint/rules.py](pgml_lint/rules.py), builds a registry via [pgml_lint/registry.py](pgml_lint/registry.py), and resolves enabled plugins.
- For each input file, [pgml_lint/engine.py](pgml_lint/engine.py) reads text, calls [pgml_lint/parser.py](pgml_lint/parser.py) helpers to build context, and gathers PGML regions and metadata.
- Each plugin inspects the shared context and emits issue dictionaries that are aggregated and sorted.
- [pgml_lint/core.py](pgml_lint/core.py) formats issue lines and computes summary counts for CLI output.

## Testing and verification

- Tests live under [tests/](tests/) and include parser behavior, lint checks, shebang and indentation validation, ASCII compliance, and pyflakes gating.

## Extension points

- Add new built-in checks by creating modules under [pgml_lint/plugins/](pgml_lint/plugins/) and registering them in [pgml_lint/plugins/__init__.py](pgml_lint/plugins/__init__.py).
- Load custom plugins from file paths with [pgml_lint/registry.py](pgml_lint/registry.py) via the registry loader.
- Extend or override default rules by supplying JSON to [pgml_lint/rules.py](pgml_lint/rules.py) in a caller that supports custom rule files.

## Known gaps

- [pyproject.toml](pyproject.toml) declares a script entry point at pgml_lint.cli:main, but there is no [pgml_lint/cli.py](pgml_lint/cli.py) module in the repo. Verify the intended CLI module path.
- [pyproject.toml](pyproject.toml) declares package data for rules/*.yaml, but there is no [pgml_lint/rules/](pgml_lint/rules/) directory in the repo. Confirm whether rule data files are expected.
