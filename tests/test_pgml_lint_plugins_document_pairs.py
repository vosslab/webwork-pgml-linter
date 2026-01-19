# Local modules
import pgml_lint.parser
import pgml_lint.plugins.document_pairs


#============================================

def test_run_no_document_returns_empty() -> None:
	context = {"stripped_text": "", "newlines": []}
	assert pgml_lint.plugins.document_pairs.run(context) == []


#============================================

def test_run_document_missing_end_warns() -> None:
	text = "DOCUMENT();\n"
	context = {
		"stripped_text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.document_pairs.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	assert issues[0]["line"] == 1


#============================================

def test_run_end_before_start_errors() -> None:
	text = "ENDDOCUMENT();\nDOCUMENT();\n"
	context = {
		"stripped_text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.document_pairs.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"
	assert issues[0]["line"] == 1


#============================================

def test_run_mismatched_counts_errors() -> None:
	text = "DOCUMENT();\nDOCUMENT();\nENDDOCUMENT();\n"
	context = {
		"stripped_text": text,
		"newlines": pgml_lint.parser.build_newline_index(text),
	}
	issues = pgml_lint.plugins.document_pairs.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"
