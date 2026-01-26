# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_include_pgproblem


#============================================

def test_warns_on_include_pgproblem() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

includePGproblem('foo/bar.pg');

BEGIN_PGML
Some text.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_include_pgproblem.run(context)
	assert len(issues) == 1
	assert "includePGproblem" in str(issues[0].get("message", ""))


#============================================

def test_warns_on_include_only_wrapper() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

includePGproblem('foo/bar.pg');

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_include_pgproblem.run(context)
	assert len(issues) == 2
	assert any("only content" in str(issue.get("message", "")) for issue in issues)
