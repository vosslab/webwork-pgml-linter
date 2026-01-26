# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_nbsp


#============================================

def test_warns_on_nbsp() -> None:
	text = "DOCUMENT();\nA\u00a0B\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_nbsp.run(context)
	assert len(issues) == 1
	assert "Non-breaking space" in str(issues[0].get("message", ""))


#============================================

def test_ignores_regular_space() -> None:
	text = "DOCUMENT();\nA B\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_nbsp.run(context)
	assert len(issues) == 0
