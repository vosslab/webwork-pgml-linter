# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_loadmacros_integrity


#============================================

def test_missing_semicolon() -> None:
	text = """DOCUMENT();
loadMacros(
  'PGstandard.pl',
  'PGML.pl'
)
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_loadmacros_integrity.run(context)
	assert any(issue["severity"] == "ERROR" for issue in issues)
	assert any("semicolon" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_missing_paren() -> None:
	text = """DOCUMENT();
loadMacros(
  'PGstandard.pl',
  'PGML.pl'
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_loadmacros_integrity.run(context)
	assert any("missing closing parenthesis" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_missing_comma() -> None:
	text = """DOCUMENT();
loadMacros(
  'PGstandard.pl'
  'PGML.pl'
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_loadmacros_integrity.run(context)
	assert any("missing a comma" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_trailing_comma_warning() -> None:
	text = """DOCUMENT();
loadMacros(
  'PGstandard.pl',
  'PGML.pl',
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_loadmacros_integrity.run(context)
	assert any(issue["severity"] == "WARNING" for issue in issues)
	assert any("trailing comma" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_valid_loadmacros() -> None:
	text = """DOCUMENT();
loadMacros(
  'PGstandard.pl',
  'PGML.pl'
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_loadmacros_integrity.run(context)
	assert len(issues) == 0
