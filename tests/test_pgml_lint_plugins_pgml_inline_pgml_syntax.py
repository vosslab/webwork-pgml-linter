# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_inline_pgml_syntax


#============================================

def test_run_warns_on_pgml_wrapper_in_inline_code() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = "[<label>]{['div']}{['','']}"; @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_pgml_syntax.run(context)
	assert len(issues) >= 1
	assert all(issue["severity"] == "ERROR" for issue in issues)


#============================================

def test_run_warns_on_nested_pgml_markers() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ "BEGIN_PGML inside inline" @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_pgml_syntax.run(context)
	assert len(issues) >= 1
	assert all(issue["severity"] == "ERROR" for issue in issues)


#============================================

def test_run_allows_safe_inline_code() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = 2 + 2; @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_inline_pgml_syntax.run(context)
	assert len(issues) == 0
