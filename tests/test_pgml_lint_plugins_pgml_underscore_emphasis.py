# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_underscore_emphasis


#============================================

def test_run_warns_on_unclosed_underscore() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is _italic text.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_underscore_emphasis.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"


#============================================

def test_run_allows_balanced_underscore() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is _italic_ text.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_underscore_emphasis.run(context)
	assert len(issues) == 0


#============================================

def test_run_ignores_math_underscores() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is [` x_1 + x_2 `] in math.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_underscore_emphasis.run(context)
	assert len(issues) == 0


#============================================

def test_run_ignores_word_underscores() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Use var_name in text.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_underscore_emphasis.run(context)
	assert len(issues) == 0
