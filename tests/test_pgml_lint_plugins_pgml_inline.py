# Local modules
import pgml_lint.parser
import pgml_lint.plugins.pgml_inline


#============================================

def test_run_sets_inline_spans_and_reports_issues() -> None:
	text = "[@ code"
	region = {"start": 0, "end": len(text)}
	context = {
		"pgml_regions": [region],
		"text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.pgml_inline.run(context)
	assert len(issues) == 1
	assert "open" in issues[0]["message"]
	assert len(context["pgml_inline_spans"]) == 1
