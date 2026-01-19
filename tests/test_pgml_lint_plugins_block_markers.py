# Local modules
import pgml_lint.plugins.block_markers


#============================================

def test_run_returns_block_marker_issues() -> None:
	issues = [{"severity": "ERROR", "message": "bad"}]
	context = {"block_marker_issues": issues}
	assert pgml_lint.plugins.block_markers.run(context) == issues
