# Install

Install provides the `pgml_lint` Python package and the `pgml-lint` CLI declared in
[pyproject.toml](../pyproject.toml).

## Requirements

- Python 3.10+ (declared in [pyproject.toml](../pyproject.toml)).

## Install steps

- Install from PyPI:

```bash
pip install webwork-pgml-linter
```

- Install from source (editable):

```bash
git clone https://github.com/vosslab/webwork-pgml-linter.git
cd webwork-pgml-linter
pip install -e .
```

## Verify install

```bash
python3 -c "import pgml_lint"
```

## Known gaps

- TODO: Confirm `pgml-lint -h` works with the packaged entry point; the module
  referenced in [pyproject.toml](../pyproject.toml) is not present in the tree.
