# Third party
import pytest

pytest.skip(
	"devel/submit_to_pypi.py performs network access, filesystem IO, and subprocess calls",
	allow_module_level=True,
)
