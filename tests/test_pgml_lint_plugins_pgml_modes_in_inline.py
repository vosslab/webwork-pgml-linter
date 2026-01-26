# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_modes_in_inline


#============================================

def test_modes_in_inline_warns() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ MODES(TeX => '', HTML => '<div>') @]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_in_inline.run(context)
	assert any("MODES()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_modes_outside_inline_ok() -> None:
	text = """DOCUMENT();
$html = MODES(TeX => '', HTML => '<div>');
BEGIN_PGML
Text only.
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_in_inline.run(context)
	assert len(issues) == 0
