# Third party
import pytest

pytest.skip(
	"devel/commit_changelog.py runs git subprocesses and writes temp files",
	allow_module_level=True,
)
