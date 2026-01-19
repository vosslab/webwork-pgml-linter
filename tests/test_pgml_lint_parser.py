# Local modules
import pgml_lint.parser


#============================================

def test_newline_index_and_pos_to_line() -> None:
	text = "a\nb\nc\n"
	newlines = pgml_lint.parser.build_newline_index(text)
	assert newlines == [1, 3, 5]
	assert pgml_lint.parser.pos_to_line(newlines, 0) == 1
	assert pgml_lint.parser.pos_to_line(newlines, 2) == 2
	assert pgml_lint.parser.pos_to_line(newlines, 4) == 3
	assert pgml_lint.parser.pos_to_line(newlines, 5) == 4


#============================================

def test_strip_comments_preserves_strings() -> None:
	text = "my $x = 1; # comment\nmy $y = '# not';\n"
	stripped = pgml_lint.parser.strip_comments(text)
	assert stripped.splitlines()[0].strip().endswith(";")
	assert "#" not in stripped.splitlines()[0]
	assert "# not" in stripped


#============================================

def test_strip_heredocs_preserves_line_count() -> None:
	text = "my $x = <<'PGML';\nLine one\nPGML\nAfter\n"
	stripped = pgml_lint.parser.strip_heredocs(text)
	assert stripped.count("\n") == text.count("\n")
	assert "Line one" not in stripped
	assert "After" in stripped


#============================================

def test_iter_calls_extracts_loadmacros() -> None:
	text = "loadMacros(\"PGML.pl\", 'foo.pl');\n"
	calls = pgml_lint.parser.iter_calls(text, {"loadMacros"})
	assert len(calls) == 1
	call = calls[0]
	assert call["name"] == "loadMacros"
	assert "PGML.pl" in call["arg_text"]
	assert call["line"] == 1


#============================================

def test_extract_loaded_macros() -> None:
	text = "loadMacros(\"PGML.pl\", 'macros/ParserPopUp.pl');\n"
	macros = pgml_lint.parser.extract_loaded_macros(text)
	assert macros == {"pgml.pl", "parserpopup.pl"}


#============================================

def test_extract_assigned_vars_includes_arrays_hashes() -> None:
	text = "my $a = 1; our @arr = (); %hash = (); $b = 2;"
	vars_found = pgml_lint.parser.extract_assigned_vars(text)
	assert vars_found == {"a", "arr", "hash", "b"}


#============================================

def test_detect_pgml_usage_signals() -> None:
	assert pgml_lint.parser.detect_pgml_usage("BEGIN_PGML\n") is True
	assert pgml_lint.parser.detect_pgml_usage("PGML::Format") is True
	assert pgml_lint.parser.detect_pgml_usage("PGML::") is True
	assert pgml_lint.parser.detect_pgml_usage("no pgml here") is False


#============================================

def test_extract_block_markers_reports_unmatched_end() -> None:
	text = "END_PGML\n"
	issues, regions = pgml_lint.parser.extract_block_markers(text)
	assert regions == []
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"
	assert issues[0]["line"] == 1


#============================================

def test_extract_block_markers_collects_regions() -> None:
	text = "BEGIN_PGML\nHello\nEND_PGML\n"
	issues, regions = pgml_lint.parser.extract_block_markers(text)
	assert issues == []
	assert len(regions) == 1
	assert regions[0]["kind"] == "BEGIN_PGML"


#============================================

def test_extract_pgml_heredoc_regions() -> None:
	text = "my $x = <<PGML;\nLine one\nPGML\n"
	issues, regions = pgml_lint.parser.extract_pgml_heredoc_regions(text)
	assert issues == []
	assert len(regions) == 1
	assert regions[0]["kind"] == "HEREDOC_PGML"


#============================================

def test_extract_pgml_heredoc_regions_missing_terminator() -> None:
	text = "my $x = <<PGML;\nLine one\n"
	issues, regions = pgml_lint.parser.extract_pgml_heredoc_regions(text)
	assert regions == []
	assert len(issues) == 1
	assert "not found" in issues[0]["message"]
