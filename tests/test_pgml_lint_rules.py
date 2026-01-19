# Third party
import pytest

# Local modules
import pgml_lint.rules


#============================================

def test_load_rules_defaults() -> None:
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	assert block_rules == pgml_lint.rules.DEFAULT_BLOCK_RULES
	assert macro_rules == pgml_lint.rules.DEFAULT_MACRO_RULES
	assert block_rules[0]["label"] == "DOCUMENT()/ENDDOCUMENT()"
	assert any("MathObjects" in rule["label"] for rule in macro_rules)


#============================================

def test_load_rules_from_file_skipped() -> None:
	pytest.skip("load_rules reads a file path, which is not allowed in unit tests", allow_module_level=False)
