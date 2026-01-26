# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_html_var_passthrough


#============================================

def test_html_var_without_star_warns() -> None:
	text = """DOCUMENT();
my $label = '<span style="color:red">Red</span>';
BEGIN_PGML
[$label]
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_var_passthrough.run(context)
	assert any("passthrough" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_html_var_with_star_ok() -> None:
	text = """DOCUMENT();
my $label = '<span style="color:red">Red</span>';
BEGIN_PGML
[$label]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_var_passthrough.run(context)
	assert len(issues) == 0


#============================================

def test_html_var_inline_ok() -> None:
	text = """DOCUMENT();
my $label = '<span style="color:red">Red</span>';
BEGIN_PGML
[@ $label @]*
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_var_passthrough.run(context)
	assert len(issues) == 0
