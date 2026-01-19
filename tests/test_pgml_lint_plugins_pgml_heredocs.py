# Local modules
import pgml_lint.plugins.pgml_heredocs


#============================================

def test_run_returns_pgml_heredoc_issues() -> None:
	issues = [{"severity": "ERROR", "message": "bad"}]
	context = {"pgml_heredoc_issues": issues}
	assert pgml_lint.plugins.pgml_heredocs.run(context) == issues
