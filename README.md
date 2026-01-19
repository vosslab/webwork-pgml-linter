# webwork-pgml-linter

A static linter for WeBWorK `.pg` problem files that checks PGML markup and common authoring mistakes for instructors and content authors.

## Documentation

- Getting started:
  - [docs/INSTALL.md](docs/INSTALL.md) - Setup and install steps.
  - [docs/USAGE.md](docs/USAGE.md) - CLI usage and examples.
- Linter docs:
  - [docs/PGML_LINT.md](docs/PGML_LINT.md) - Linter overview and quick start.
  - [docs/PGML_LINT_CONCEPTS.md](docs/PGML_LINT_CONCEPTS.md) - PGML syntax concepts.
  - [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md) - Built-in plugin reference.
  - [docs/PGML_LINT_PLUGIN_DEV.md](docs/PGML_LINT_PLUGIN_DEV.md) - Writing custom plugins.
- Project docs:
  - [docs/CODE_ARCHITECTURE.md](docs/CODE_ARCHITECTURE.md) - Code architecture overview.
  - [docs/FILE_STRUCTURE.md](docs/FILE_STRUCTURE.md) - Repo file structure map.
  - [docs/CHANGELOG.md](docs/CHANGELOG.md) - Release history.

## Quick start

```bash
# Check a single file
pgml-lint -i path/to/file.pg

# Check all .pg files in a directory
pgml-lint -d problems/
```

## Testing

```bash
python3 -m pytest tests/
```

## License

Licensed under the [GNU Lesser General Public License v2.1](LICENSE).

## Author

Neil R. Voss - https://bsky.app/profile/neilvosslab.bsky.social
