# Third party
import pytest

# Local modules
import pgml_lint.engine


#============================================

def test_build_context_pgml_detection() -> None:
	text = "DOCUMENT();\n# comment\nloadMacros(\"PGML.pl\");\nBEGIN_PGML\nHello\nEND_PGML\n"
	block_rules: list[dict[str, str]] = []
	macro_rules: list[dict[str, object]] = []
	context = pgml_lint.engine.build_context(text, "file.pg", block_rules, macro_rules)
	assert context["file_path"] == "file.pg"
	assert "pgml.pl" in context["macros_loaded"]
	assert context["uses_pgml"] is True
	assert len(context["pgml_regions"]) == 1
	assert context["pgml_heredoc_regions"] == []


#============================================

def test_run_plugins_adds_plugin_id_and_sorts() -> None:
	context: dict[str, object] = {}

	issues_a = [{"severity": "WARNING", "message": "b", "line": 2}]
	issues_b = [{"severity": "WARNING", "message": "a", "line": 1, "plugin": "preset"}]

	def run_a(_context: dict[str, object]) -> list[dict[str, object]]:
		return issues_a

	def run_b(_context: dict[str, object]) -> list[dict[str, object]]:
		return issues_b

	plugins = [
		{"id": "plug_a", "run": run_a},
		{"id": "plug_b", "run": run_b},
	]
	results = pgml_lint.engine.run_plugins(context, plugins)
	assert results[0]["message"] == "a"
	assert results[0]["plugin"] == "preset"
	assert results[1]["message"] == "b"
	assert results[1]["plugin"] == "plug_a"


#============================================

def test_lint_text_uses_plugins() -> None:
	text = "BEGIN_PGML\nHello\nEND_PGML\n"
	block_rules: list[dict[str, str]] = []
	macro_rules: list[dict[str, object]] = []

	def run_plugin(context: dict[str, object]) -> list[dict[str, object]]:
		assert context["uses_pgml"] is True
		return [{"severity": "WARNING", "message": "note", "line": 1}]

	plugins = [{"id": "p", "run": run_plugin}]
	issues = pgml_lint.engine.lint_text(text, None, block_rules, macro_rules, plugins)
	assert issues == [{"severity": "WARNING", "message": "note", "line": 1, "plugin": "p"}]


#============================================

def test_lint_file_skipped() -> None:
	pytest.skip("lint_file reads files from disk, which is not allowed in unit tests", allow_module_level=False)
