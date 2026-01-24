# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_html_in_text


#============================================

def test_run_warns_on_html_tags_in_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This has <strong>bold</strong> and <em>italic</em> text.
Also <sub>subscript</sub> and <sup>superscript</sup>.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) == 4
	assert all(issue["severity"] == "WARNING" for issue in issues)
	assert any("strong" in str(issue.get("message", "")) for issue in issues)
	assert any("em" in str(issue.get("message", "")) for issue in issues)
	assert any("sub" in str(issue.get("message", "")) for issue in issues)
	assert any("sup" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_run_warns_on_html_entities() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This has &nbsp; and &lt; and &copy; entities.
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) == 3
	assert all("entity" in str(issue.get("message", "")).lower() for issue in issues)


#============================================

def test_run_ignores_html_in_inline_code() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is okay: [@ '<strong>generated HTML</strong>' @]*
END_PGML

ENDDOCUMENT();
"""
	# Local modules
	import pgml_lint.plugins.pgml_inline

	context = pgml_lint.engine.build_context(text, None, [], [])
	# First run pgml_inline plugin to set up inline spans
	pgml_lint.plugins.pgml_inline.run(context)
	# Now run the HTML detection plugin
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) == 0


#============================================

def test_run_no_warning_outside_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

# This is in Perl code, not PGML
$html = '<strong>bold</strong>';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_br_and_p_tags() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Line one<br>
Line two

<p>Paragraph text</p>
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) >= 2
	assert any("br" in str(issue.get("message", "")).lower() for issue in issues)
	assert any("<p>" in str(issue.get("message", "")).lower() for issue in issues)


#============================================

def test_run_detects_table_tags() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
<table>
<tr><td>Cell</td></tr>
</table>
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) >= 3
	assert any("table" in str(issue.get("message", "")).lower() for issue in issues)
	assert any("DataTable" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_run_detects_multiple_regions() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
First block with <strong>bold</strong>.
END_PGML

BEGIN_PGML_SOLUTION
Solution with <em>italic</em>.
END_PGML_SOLUTION

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_html_in_text.run(context)
	assert len(issues) == 2
