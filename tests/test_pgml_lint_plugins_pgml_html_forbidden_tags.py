# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_html_forbidden_tags


#============================================

def test_run_warns_on_table_tags_in_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
<table><tr><td>Cell</td></tr></table>
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_forbidden_tags.run(context)
	assert len(issues) >= 3
	assert all(issue["severity"] == "ERROR" for issue in issues)


#============================================

def test_run_warns_on_table_tags_in_inline_code() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ MODES(TeX => '', HTML => '<table><tr><td>X</td></tr></table>') @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_forbidden_tags.run(context)
	assert len(issues) >= 3
	assert all(issue["severity"] == "ERROR" for issue in issues)


#============================================

def test_run_ignores_table_tags_outside_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = '<table><tr><td>Cell</td></tr></table>';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_forbidden_tags.run(context)
	assert len(issues) == 0
