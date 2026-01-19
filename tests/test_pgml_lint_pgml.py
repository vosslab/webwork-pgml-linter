# Local modules
import pgml_lint.parser
import pgml_lint.pgml


#============================================

def test_extract_inline_spans_balanced() -> None:
	block_text = "Alpha [@ code @] omega"
	newlines = pgml_lint.parser.build_newline_index(block_text)
	issues, spans = pgml_lint.pgml.extract_inline_spans(block_text, 0, newlines)
	assert issues == []
	assert len(spans) == 1


#============================================

def test_extract_inline_spans_unbalanced_open() -> None:
	block_text = "Alpha [@ code"
	newlines = pgml_lint.parser.build_newline_index(block_text)
	issues, spans = pgml_lint.pgml.extract_inline_spans(block_text, 0, newlines)
	assert spans == []
	assert len(issues) == 1
	assert "open" in issues[0]["message"]


#============================================

def test_scan_pgml_blanks_extracts_vars() -> None:
	block_text = "[_]{ $ans }"
	newlines = pgml_lint.parser.build_newline_index(block_text)
	issues, vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
		block_text,
		0,
		newlines,
		[],
	)
	assert issues == []
	assert vars_found == {"ans"}
	assert len(blank_spans) == 1


#============================================

def test_scan_pgml_blanks_missing_spec_warns() -> None:
	block_text = "[_]"
	newlines = pgml_lint.parser.build_newline_index(block_text)
	issues, vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
		block_text,
		0,
		newlines,
		[],
	)
	assert vars_found == set()
	assert len(blank_spans) == 1
	assert len(issues) == 1
	assert "missing answer spec" in issues[0]["message"]


#============================================

def test_check_pgml_bracket_balance_reports_unmatched() -> None:
	block_text = "Text ["
	newlines = pgml_lint.parser.build_newline_index(block_text)
	issues = pgml_lint.pgml.check_pgml_bracket_balance(
		block_text,
		0,
		newlines,
		[],
		[],
	)
	assert len(issues) == 1
	assert "open" in issues[0]["message"]


#============================================

def test_check_pgml_bracket_balance_ignores_masks() -> None:
	block_text = "[@ [ @] [_]{a} [`x]` [:y:]"
	newlines = pgml_lint.parser.build_newline_index(block_text)
	inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
		block_text,
		0,
		newlines,
	)
	assert inline_issues == []
	blank_issues, _vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
		block_text,
		0,
		newlines,
		inline_spans,
	)
	assert blank_issues == []
	issues = pgml_lint.pgml.check_pgml_bracket_balance(
		block_text,
		0,
		newlines,
		inline_spans,
		blank_spans,
	)
	assert issues == []
