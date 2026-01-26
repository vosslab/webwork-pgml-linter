# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_span_interpolation


#============================================

def test_run_warns_when_span_var_not_interpolated() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $answers_html = '<span class="ok">Hi</span>';

BEGIN_PGML
No interpolation here.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_span_interpolation.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"


#============================================

def test_run_allows_span_var_interpolation() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $answers_html = '<span class="ok">Hi</span>';

BEGIN_PGML
Here: [$answers_html]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_span_interpolation.run(context)
	assert len(issues) == 0
