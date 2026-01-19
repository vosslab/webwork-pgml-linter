# Usage

Use the CLI to lint WeBWorK `.pg` files for PGML markup issues; for deeper
coverage see [docs/PGML_LINT.md](PGML_LINT.md).

## Quick start

```bash
# Check a single file
pgml-lint -i path/to/file.pg

# Check all .pg files in a directory
pgml-lint -d problems/

# Verbose output
pgml-lint -v -i file.pg
```

## CLI

- Packaged entry point (declared in [pyproject.toml](../pyproject.toml)):
  `pgml-lint`
- Repo script: [tools/webwork_pgml_simple_lint.py](../tools/webwork_pgml_simple_lint.py)

Common flags:

- `-i`, `--input`: Check a single `.pg` file.
- `-d`, `--directory`: Check all `.pg` files in a directory.
- `-v`, `--verbose`: Show active checks and summary details.
- `-q`, `--quiet`: Suppress summary output.
- `--json`: Emit a JSON summary to stdout.

## Examples

```bash
# Quiet mode over a directory
pgml-lint -q -d problems/
```

```bash
# JSON output for scripting
pgml-lint --json -i path/to/file.pg > report.json
```

## Inputs and outputs

- Inputs: `.pg` files or directories containing `.pg` files.
- Outputs: line-oriented issue reports or JSON summaries to stdout; exit code 1
  when errors are detected.

## Known gaps

- TODO: Confirm the packaged CLI module for `pgml-lint` exists and works as
  declared in [pyproject.toml](../pyproject.toml).
