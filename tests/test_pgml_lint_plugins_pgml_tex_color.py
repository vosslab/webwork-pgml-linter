# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_tex_color


#============================================

def test_warns_on_tex_color() -> None:
	text = """DOCUMENT();

BEGIN_PGML
This is [\\color{red}{text}].
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_tex_color.run(context)
	assert len(issues) == 1
	assert "TeX color commands" in str(issues[0].get("message", ""))


#============================================

def test_ignores_when_no_color() -> None:
	text = """DOCUMENT();
BEGIN_PGML
Plain text.
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_tex_color.run(context)
	assert len(issues) == 0
