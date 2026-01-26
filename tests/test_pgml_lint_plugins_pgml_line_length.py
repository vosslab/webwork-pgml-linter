# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_line_length


#============================================

def test_warns_on_long_line() -> None:
	long_line = "A" * 201
	text = f"{long_line}\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_line_length.run(context)
	assert len(issues) == 1
	assert "Line length" in str(issues[0].get("message", ""))


#============================================

def test_warns_on_extreme_line_without_whitespace() -> None:
	long_line = "B" * 401
	text = f"{long_line}\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_line_length.run(context)
	assert len(issues) == 2
	assert any("Line length" in str(issue.get("message", "")) for issue in issues)
	assert any("Long line without whitespace" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_ignores_short_line() -> None:
	text = "short line\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_line_length.run(context)
	assert len(issues) == 0
