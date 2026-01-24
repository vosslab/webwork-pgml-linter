# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_inline
import pgml_lint.plugins.pgml_modes_html_escape


#============================================

def test_run_warns_on_modes_html_in_bracket_interp() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = MODES(TeX => 'text', HTML => '<span>formatted</span>');

BEGIN_PGML
This will escape: [$html]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first to set up spans
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "MODES()" in message
	assert "[$var]" in message or "interpolation" in message
	assert "[@ $" in message
	assert "escapes HTML" in message


#============================================

def test_run_no_warning_with_inline_code_syntax() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = MODES(TeX => 'text', HTML => '<span>formatted</span>');

BEGIN_PGML
This is correct: [@ $html @]*
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first to set up spans
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 0


#============================================

def test_run_no_warning_when_no_modes_html() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$var = "plain text";

BEGIN_PGML
This is fine: [$var]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_modes_with_tex_mode() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$formatted = MODES(
	TeX => '\\\\textbf{text}',
	HTML => '<strong>text</strong>'
);

BEGIN_PGML
Problem: [$formatted]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 1


#============================================

def test_run_multiple_vars_multiple_uses() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html1 = MODES(TeX => 'a', HTML => '<span>a</span>');
$html2 = MODES(TeX => 'b', HTML => '<em>b</em>');

BEGIN_PGML
First: [$html1]
Second: [$html2]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 2


#============================================

def test_run_mixed_correct_and_incorrect() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = MODES(TeX => 'text', HTML => '<b>text</b>');

BEGIN_PGML
Correct: [@ $html @]*

Incorrect: [$html]
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	# Should only warn about the incorrect one
	assert len(issues) == 1
	assert issues[0]["line"] == 9


#============================================

def test_run_no_warning_outside_pgml() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$html = MODES(TeX => 'text', HTML => '<span>text</span>');

# Using outside PGML is fine (different context)
$other = "Value: $html";

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	# Run inline plugin first
	pgml_lint.plugins.pgml_inline.run(context)
	# Run MODES HTML escape detection
	issues = pgml_lint.plugins.pgml_modes_html_escape.run(context)
	assert len(issues) == 0
