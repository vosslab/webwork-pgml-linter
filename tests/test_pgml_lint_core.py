# Local modules
import pgml_lint.core


#============================================

def test_make_issue_basic() -> None:
	issue = pgml_lint.core.make_issue("ERROR", "bad")
	assert issue == {"severity": "ERROR", "message": "bad"}


#============================================

def test_make_issue_with_line_and_plugin() -> None:
	issue = pgml_lint.core.make_issue("WARNING", "msg", line=5, plugin="plug")
	assert issue["severity"] == "WARNING"
	assert issue["message"] == "msg"
	assert issue["line"] == 5
	assert issue["plugin"] == "plug"


#============================================

def test_summarize_issues_counts_errors_and_warnings() -> None:
	issues = [
		{"severity": pgml_lint.core.SEVERITY_ERROR, "message": "a"},
		{"severity": "WARNING", "message": "b"},
		{"severity": "WARNING", "message": "c"},
	]
	errors, warnings = pgml_lint.core.summarize_issues(issues)
	assert errors == 1
	assert warnings == 2


#============================================

def test_format_issue_without_line() -> None:
	issue = {"severity": "WARNING", "message": "note"}
	formatted = pgml_lint.core.format_issue("file.pg", issue, show_plugin=False)
	assert formatted == "file.pg: WARNING: note"


#============================================

def test_format_issue_with_line_and_plugin() -> None:
	issue = {"severity": "ERROR", "message": "bad", "line": 10, "plugin": "x"}
	formatted = pgml_lint.core.format_issue("file.pg", issue, show_plugin=True)
	assert formatted == "file.pg:10: ERROR(x): bad"


#============================================

def test_format_issue_with_line_no_plugin() -> None:
	issue = {"severity": "ERROR", "message": "bad", "line": 10}
	formatted = pgml_lint.core.format_issue("file.pg", issue, show_plugin=True)
	assert formatted == "file.pg:10: ERROR: bad"


#============================================

def test_format_issue_with_excerpt_verbose() -> None:
	issue = {
		"severity": "ERROR",
		"message": "bad",
		"line": 10,
		"plugin": "x",
		"excerpt": "...oops...",
	}
	formatted = pgml_lint.core.format_issue("file.pg", issue, show_plugin=True)
	assert formatted == "file.pg:10: ERROR(x): bad | context: ...oops..."
