# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_br_variable


#============================================

def test_run_warns_on_br_variable() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
Line one
$BR
Line two
END_TEXT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_br_variable.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "$BR" in message
	assert "deprecated" in message.lower()


#============================================

def test_run_no_warning_with_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Line one

Line two
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_br_variable.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_multiple_br_variables() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
Paragraph one
$BR
Paragraph two
$BR
Paragraph three
END_TEXT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_br_variable.run(context)
	assert len(issues) == 2


#============================================

def test_run_ignores_br_in_comments() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

# Old way: $BR for line breaks
# Don't use $BR anymore

BEGIN_PGML
Modern way: blank lines
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_br_variable.run(context)
	# Comments are stripped, so no issues
	assert len(issues) == 0


#============================================

def test_run_detects_br_in_concatenation() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

$text = "Line one" . $BR . "Line two";

BEGIN_TEXT
$text
END_TEXT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_br_variable.run(context)
	assert len(issues) == 1
