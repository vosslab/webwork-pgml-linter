# Third party
import pytest

pytest.skip(
	"tools/webwork_pgml_simple_lint.py runs subprocess git calls at import and does file IO",
	allow_module_level=True,
)
