# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_modes_in_inline


#============================================

def test_modes_in_inline_warns_for_non_217() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ MODES(TeX => '', HTML => '<div>') @]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.18")
	issues = pgml_lint.plugins.pgml_modes_in_inline.run(context)
	assert any("MODES()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_modes_in_inline_allows_217_layout() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ MODES(TeX => '', HTML => '<div class="two-column">') @]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.17")
	issues = pgml_lint.plugins.pgml_modes_in_inline.run(context)
	assert issues == []


#============================================

def test_modes_in_inline_requires_empty_tex_for_217_layout() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ MODES(TeX => 'x', HTML => '<div class="two-column">') @]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.17")
	issues = pgml_lint.plugins.pgml_modes_in_inline.run(context)
	assert any("TeX => ''" in str(issue.get("message", "")) for issue in issues)


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
