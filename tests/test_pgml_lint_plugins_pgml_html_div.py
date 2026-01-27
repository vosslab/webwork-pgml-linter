# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_html_div


#============================================

def test_run_warns_on_div_in_pgml_text() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Here is a <div class="bad">block</div>.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.18")
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert len(issues) == 2
	assert all(issue["severity"] == "ERROR" for issue in issues)


#============================================

def test_run_allows_div_in_pgml_text_for_217() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Here is a <div class="ok">block</div>.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.17")
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert issues == []


#============================================

def test_run_warns_on_div_in_inline_code() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ MODES(TeX => '', HTML => '<div class="two-column">') @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.18")
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"


#============================================

def test_run_allows_div_in_inline_code_for_217() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ MODES(TeX => '', HTML => '<div class="two-column">') @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.17")
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert issues == []


#============================================

def test_run_warns_on_escaped_div() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This shows &lt;div class="two-column"&gt; text.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [], pg_version="2.17")
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"


#============================================

def test_run_ignores_div_outside_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = '<div class="ok"></div>';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_div.run(context)
	assert len(issues) == 0
