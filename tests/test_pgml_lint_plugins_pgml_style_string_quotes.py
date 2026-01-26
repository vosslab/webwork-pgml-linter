# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_style_string_quotes


#============================================

def test_run_warns_on_unescaped_quotes_in_style_string() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

%match_data = (
  '[<bond>]{['span', style => 'color: #00b3b3;']}{['','']}' => [
    'H - O - H',
  ],
);

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_style_string_quotes.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"
	assert "single-quoted" in str(issues[0].get("message", ""))


#============================================

def test_run_allows_escaped_quotes_in_style_string() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

%match_data = (
  '[<bond>]{[\\'span\\', style => \\'color: #00b3b3;\\']}{[\\'\\',\\'\\']}' => [
    'H - O - H',
  ],
);

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_style_string_quotes.run(context)
	assert len(issues) == 0


#============================================

def test_run_allows_double_quoted_style_string() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

%match_data = (
  "[<bond>]{['span', style => 'color: #00b3b3;']}{['','']}" => [
    'H - O - H',
  ],
);

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_style_string_quotes.run(context)
	assert len(issues) == 0


#============================================

def test_run_ignores_pgml_block_content() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[<bond>]{['span', style => 'color: #00b3b3;']}{['','']}
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_style_string_quotes.run(context)
	assert len(issues) == 0
