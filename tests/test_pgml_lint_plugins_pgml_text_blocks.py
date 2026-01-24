# Local modules
import pgml_lint.parser
import pgml_lint.plugins.pgml_text_blocks


#============================================

def test_run_warns_when_begin_text_present() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
This is deprecated text block syntax.
END_TEXT

ENDDOCUMENT();
"""
	newlines = pgml_lint.parser.build_newline_index(text)
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_text_blocks.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "deprecated" in message.lower()
	assert "BEGIN_TEXT" in message
	assert issues[0]["line"] == 4


#============================================

def test_run_warns_for_multiple_text_blocks() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
First block.
END_TEXT

BEGIN_TEXT
Second block.
END_TEXT

ENDDOCUMENT();
"""
	newlines = pgml_lint.parser.build_newline_index(text)
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_text_blocks.run(context)
	assert len(issues) == 2
	assert issues[0]["line"] == 4
	assert issues[1]["line"] == 8


#============================================

def test_run_no_warning_when_only_pgml_used() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is modern PGML syntax.
END_PGML

ENDDOCUMENT();
"""
	newlines = pgml_lint.parser.build_newline_index(text)
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_text_blocks.run(context)
	assert issues == []


#============================================

def test_run_ignores_text_in_comments() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

# BEGIN_TEXT is deprecated
# Don't use BEGIN_TEXT anymore

BEGIN_PGML
Modern PGML content.
END_PGML

ENDDOCUMENT();
"""
	newlines = pgml_lint.parser.build_newline_index(text)
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_text_blocks.run(context)
	# The regex requires BEGIN_TEXT at start of line (after optional whitespace)
	# so commented BEGIN_TEXT won't match - this is correct behavior
	assert len(issues) == 0


#============================================

def test_run_detects_indented_text_blocks() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

	BEGIN_TEXT
	Indented text block.
	END_TEXT

ENDDOCUMENT();
"""
	newlines = pgml_lint.parser.build_newline_index(text)
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_text_blocks.run(context)
	assert len(issues) == 1
	assert issues[0]["line"] == 4
