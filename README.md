# webwork-pgml-linter

A static linter for WeBWorK `.pg` problem files that checks PGML markup, common authoring mistakes, and style issues. Works offline without requiring the PG library.

## Installation

```bash
pip install webwork-pgml-linter
```

Or install from source:

```bash
git clone https://github.com/vosslab/webwork-pgml-linter.git
cd webwork-pgml-linter
pip install -e .
```

## Quick Start

```bash
# Check a single file
pgml-lint -i path/to/file.pg

# Check all .pg files in a directory
pgml-lint -d problems/

# Verbose output
pgml-lint -v -i file.pg

# Quiet mode (only errors/warnings)
pgml-lint -q -d problems/
```

## What the Linter Checks

- **PGML block structure**: BEGIN_PGML/END_PGML pairing, nesting errors
- **DOCUMENT pairing**: DOCUMENT()/ENDDOCUMENT() balance
- **PGML heredocs**: Unterminated heredoc detection
- **Inline code markers**: `[@` and `@]` balance
- **Answer blank syntax**: Missing answer specs, unbalanced braces
- **Required macros**: PGML.pl loading when PGML is used
- **Macro coverage**: Functions used without required macro files
- **Variable assignments**: Blanks referencing undefined variables

## Documentation

- [docs/PGML_LINT.md](docs/PGML_LINT.md) - Usage guide and quick start
- [docs/PGML_LINT_CONCEPTS.md](docs/PGML_LINT_CONCEPTS.md) - PGML syntax concepts
- [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md) - Built-in plugin reference
- [docs/PGML_LINT_PLUGIN_DEV.md](docs/PGML_LINT_PLUGIN_DEV.md) - Writing custom plugins
- [docs/PGML_LINT_ARCHITECTURE.md](docs/PGML_LINT_ARCHITECTURE.md) - Internal architecture

## License

Licensed under the [GNU Lesser General Public License v2.1](LICENSE).

## Author

Neil R. Voss - https://bsky.app/profile/neilvosslab.bsky.social
