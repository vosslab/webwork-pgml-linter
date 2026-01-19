# Local modules
import pgml_lint.parser
import pgml_lint.plugins.pgml_brackets


#============================================

def test_run_reports_unmatched_brackets() -> None:
	text = "Text ["
	region = {"start": 0, "end": len(text)}
	context = {
		"pgml_regions": [region],
		"text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.pgml_brackets.run(context)
	assert len(issues) == 1
	assert "open" in issues[0]["message"]


#============================================

def test_run_no_issues_for_balanced_brackets() -> None:
	text = "[good]"
	region = {"start": 0, "end": len(text)}
	context = {
		"pgml_regions": [region],
		"text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.pgml_brackets.run(context)
	assert issues == []
