# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_modes_html_plain_text


#============================================

def test_modes_html_plain_text_warns_on_plain_text() -> None:
	text = """DOCUMENT();
$label = MODES(
	TeX => '',
	HTML => 'COOH',
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_html_plain_text.run(context)
	assert any("no HTML tags" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_modes_html_plain_text_allows_html_tags() -> None:
	text = """DOCUMENT();
$label = MODES(
	TeX => '',
	HTML => '<span>COOH</span>',
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_html_plain_text.run(context)
	assert issues == []


#============================================

def test_modes_html_plain_text_warns_with_non_empty_tex() -> None:
	text = """DOCUMENT();
$label = MODES(
	TeX => 'COOH',
	HTML => 'COOH',
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_html_plain_text.run(context)
	assert any("no HTML tags" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_modes_html_plain_text_skips_variable_html() -> None:
	text = """DOCUMENT();
$label = MODES(
	TeX => '',
	HTML => $html_label,
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_html_plain_text.run(context)
	assert issues == []


#============================================

def test_modes_html_plain_text_warns_on_plain_q_string() -> None:
	text = """DOCUMENT();
$label = MODES(
	TeX => q{},
	HTML => q{COOH},
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_html_plain_text.run(context)
	assert any("no HTML tags" in str(issue.get("message", "")) for issue in issues)
