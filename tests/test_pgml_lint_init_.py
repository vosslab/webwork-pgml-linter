# Local modules
import pgml_lint


#============================================

def test_init_exports() -> None:
	expected = {
		"build_context",
		"run_plugins",
		"lint_text",
		"lint_file",
		"build_registry",
		"load_rules",
		"DEFAULT_BLOCK_RULES",
		"DEFAULT_MACRO_RULES",
	}
	assert hasattr(pgml_lint, "__all__")
	assert expected.issubset(set(pgml_lint.__all__))
	for name in expected:
		assert hasattr(pgml_lint, name)


#============================================

def test_init_all_is_list() -> None:
	assert isinstance(pgml_lint.__all__, list)
