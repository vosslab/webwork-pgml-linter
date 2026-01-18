# Standard Library
import json


DEFAULT_BLOCK_RULES: list[dict[str, str]] = [
	{
		"label": "DOCUMENT()/ENDDOCUMENT()",
		"start_pattern": r"\bDOCUMENT\s*\(\s*\)",
		"end_pattern": r"\bENDDOCUMENT\s*\(\s*\)",
	},
]

DEFAULT_MACRO_RULES: list[dict[str, object]] = [
	{
		# PGML.pl loads MathObjects.pl internally, so either satisfies this rule
		"label": "MathObjects functions",
		"pattern": r"\b(?:Context|Compute|Formula|Real)\s*\(",
		"required_macros": ["MathObjects.pl", "PGML.pl"],
	},
	{
		"label": "RadioButtons",
		"pattern": r"\bRadioButtons\s*\(",
		"required_macros": ["parserRadioButtons.pl", "PGchoicemacros.pl"],
	},
	{
		"label": "CheckboxList",
		"pattern": r"\bCheckboxList\s*\(",
		"required_macros": ["parserCheckboxList.pl", "PGchoicemacros.pl"],
	},
	{
		"label": "PopUp",
		"pattern": r"\bPopUp\s*\(",
		"required_macros": ["parserPopUp.pl", "PGchoicemacros.pl"],
	},
	{
		"label": "DataTable",
		"pattern": r"\bDataTable\s*\(",
		"required_macros": ["niceTables.pl"],
	},
	{
		"label": "LayoutTable",
		"pattern": r"\bLayoutTable\s*\(",
		"required_macros": ["niceTables.pl"],
	},
	{
		"label": "NumberWithUnits",
		"pattern": r"\bNumberWithUnits\s*\(",
		"required_macros": ["parserNumberWithUnits.pl", "contextUnits.pl"],
	},
	{
		"label": "Context('Fraction')",
		"pattern": r"\bContext\s*\(\s*['\"]Fraction['\"]\s*\)",
		"required_macros": ["contextFraction.pl"],
	},
	{
		"label": "DraggableSubsets",
		"pattern": r"\bDraggableSubsets\s*\(",
		"required_macros": ["draggableSubsets.pl"],
	},
]


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
