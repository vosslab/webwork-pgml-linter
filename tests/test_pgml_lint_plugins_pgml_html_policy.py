# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_html_policy


#============================================

def test_script_tag_error() -> None:
	text = """DOCUMENT();
BEGIN_PGML
<script>alert("x");</script>
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any(issue["severity"] == "ERROR" for issue in issues)
	assert any("<script>" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_table_tag_in_modes_error() -> None:
	text = """DOCUMENT();
HEADER_TEXT(MODES(HTML => '<table><tr><td>1</td></tr></table>'));
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any(issue["severity"] == "ERROR" for issue in issues)
	assert any("<table>" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_form_tag_warning() -> None:
	text = """DOCUMENT();
BEGIN_PGML
<form action="/submit"></form>
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any(issue["severity"] == "WARNING" for issue in issues)


#============================================

def test_style_outside_header_text() -> None:
	text = """DOCUMENT();
<style>.bad { color: red; }</style>
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any("style" in str(issue.get("message", "")).lower() for issue in issues)


#============================================

def test_tex2jax_ignore_warning() -> None:
	text = """DOCUMENT();
BEGIN_PGML
<span class="tex2jax_ignore">\\</span>
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any("tex2jax_ignore" in str(issue.get("message", "")).lower() for issue in issues)


#============================================

def test_pgml_wrapper_disallowed_tag() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[<Table>]{['table']}{['','']}
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_policy.run(context)
	assert any("tag wrapper" in str(issue.get("message", "")).lower() for issue in issues)
