# Standard Library
import json

# Local modules
import pgml_lint.function_to_macro_pairs


DEFAULT_BLOCK_RULES: list[dict[str, str]] = [
	{
		"label": "DOCUMENT()/ENDDOCUMENT()",
		"start_pattern": r"\bDOCUMENT\s*\(\s*\)",
		"end_pattern": r"\bENDDOCUMENT\s*\(\s*\)",
	},
]

DEFAULT_MACRO_RULES: list[dict[str, object]] = (
	pgml_lint.function_to_macro_pairs.DEFAULT_MACRO_RULES
)


#============================================


def load_rules(rules_file: str | None) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
	"""
	Load block and macro rules from JSON or fall back to defaults.

	Args:
		rules_file: Optional path to a JSON rules file.

	Returns:
		tuple[list[dict[str, str]], list[dict[str, object]]]: Block and macro rules.
	"""
	if rules_file is None:
		block_rules = DEFAULT_BLOCK_RULES
		macro_rules = DEFAULT_MACRO_RULES
		return block_rules, macro_rules
	with open(rules_file, "r", encoding="utf-8") as handle:
		data = json.load(handle)
	block_rules = data.get("block_rules", DEFAULT_BLOCK_RULES)
	macro_rules = data.get("macro_rules", DEFAULT_MACRO_RULES)
	return block_rules, macro_rules
