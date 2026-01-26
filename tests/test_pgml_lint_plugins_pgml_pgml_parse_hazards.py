# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_pgml_parse_hazards


#============================================

def test_inline_paren_mismatch() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ my $x = (1 + 2; @]
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_pgml_parse_hazards.run(context)
	assert any("unbalanced parentheses" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_unknown_block_token() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[balance]
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_pgml_parse_hazards.run(context)
	assert any("Unknown PGML block token" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_balanced_inline_parens_ok() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[@ my $x = (1 + 2); @]
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_pgml_parse_hazards.run(context)
	assert len(issues) == 0
