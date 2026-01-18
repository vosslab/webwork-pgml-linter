# Local modules
import pgml_lint.engine
import pgml_lint.registry
import pgml_lint.rules


#============================================


def _run_lint(text: str) -> list[dict[str, object]]:
	"""
	Run the PGML lint engine on a text blob.
	"""
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())
	issues = pgml_lint.engine.lint_text(text, None, block_rules, macro_rules, plugins)
	return issues


#============================================


def test_pgml_blank_missing_spec() -> None:
	text = "BEGIN_PGML\nAnswer: [_]\nEND_PGML\n"
	issues = _run_lint(text)
	assert any("blank missing answer spec" in issue["message"] for issue in issues)


def test_pgml_heredoc_terminator_missing() -> None:
	text = "PGML::Format(<<END_PGML);\nAnswer: [_]{1}\n"
	issues = _run_lint(text)
	assert any("terminator" in issue["message"] for issue in issues)


def test_pgml_blank_assignment_missing() -> None:
	text = "BEGIN_PGML\nAnswer: [_]{$ans1}\nEND_PGML\n"
	issues = _run_lint(text)
	assert any("without assignment" in issue["message"] for issue in issues)
