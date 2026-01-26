# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_pgml_wrapper_in_string


#============================================

def test_pgml_wrapper_in_string_warns() -> None:
	text = """DOCUMENT();
my $label = "[<foo>]{['span']}{['','']}";
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_pgml_wrapper_in_string.run(context)
	assert any("wrapper" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_pgml_wrapper_not_in_string_ok() -> None:
	text = """DOCUMENT();
my $label = "plain text";
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_pgml_wrapper_in_string.run(context)
	assert len(issues) == 0
