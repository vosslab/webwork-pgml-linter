# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_mojibake


#============================================

def test_warns_on_mojibake_sequence() -> None:
	text = "DOCUMENT();\nCafe\u00c3\u00a9\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_mojibake.run(context)
	assert len(issues) == 1
	assert "mojibake" in str(issues[0].get("message", "")).lower()


#============================================

def test_warns_on_replacement_char() -> None:
	text = "DOCUMENT();\nBad\ufffdChar\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_mojibake.run(context)
	assert len(issues) == 1


#============================================

def test_warns_on_common_mojibake_sequences() -> None:
	text = "DOCUMENT();\nBad\u00c2Char\nBad\u00c3Char\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_mojibake.run(context)
	assert len(issues) == 2


#============================================

def test_warns_on_curly_quote_mojibake() -> None:
	text = "DOCUMENT();\nBad\u00e2\u0080\u0099Quote\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_mojibake.run(context)
	assert len(issues) == 1
