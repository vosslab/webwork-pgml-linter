# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_inline_braces


#============================================

def test_run_warns_on_unclosed_brace() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = { foo => 1; @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_braces.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"


#============================================

def test_run_warns_on_unbalanced_close_brace() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = 1; } @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_braces.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"


#============================================

def test_run_allows_balanced_braces() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = { foo => 1 }; @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_braces.run(context)
	assert len(issues) == 0


#============================================

def test_run_ignores_braces_in_strings() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = "{ not a brace }"; @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_braces.run(context)
	assert len(issues) == 0
