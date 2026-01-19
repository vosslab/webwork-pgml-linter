# Local modules
import pgml_lint.parser
import pgml_lint.plugins.pgml_blanks


#============================================

def test_run_sets_blank_vars_and_spans() -> None:
	text = "[_]{ $ans }"
	region = {"start": 0, "end": len(text)}
	context = {
		"pgml_regions": [region],
		"text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.pgml_blanks.run(context)
	assert issues == []
	assert context["pgml_blank_vars"] == {"ans"}
	assert len(context["pgml_blank_spans"]) == 1
