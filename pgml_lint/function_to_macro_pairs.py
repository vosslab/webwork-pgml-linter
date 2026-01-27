# Default function-to-macro mapping rules for macro_rules checks.

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
		"required_macros": [
			"parserRadioButtons.pl",
			"parserMultipleChoice.pl",
			"PGchoicemacros.pl",
		],
	},
	{
		"label": "CheckboxList",
		"pattern": r"\bCheckboxList\s*\(",
		"min_pg_version": "2.18",
		"required_macros": [
			"parserCheckboxList.pl",
			"parserMultipleChoice.pl",
			"PGchoicemacros.pl",
		],
	},
	{
		"label": "PopUp",
		"pattern": r"\bPopUp\s*\(",
		"required_macros": [
			"parserPopUp.pl",
			"parserMultipleChoice.pl",
			"PGchoicemacros.pl",
		],
	},
	{
		"label": "DropDown",
		"pattern": r"\bDropDown\s*\(",
		"min_pg_version": "2.18",
		"required_macros": [
			"parserPopUp.pl",
			"parserMultipleChoice.pl",
			"PGchoicemacros.pl",
		],
	},
	{
		"label": "MultiAnswer",
		"pattern": r"\bMultiAnswer\s*\(",
		"required_macros": ["parserMultiAnswer.pl"],
	},
	{
		"label": "OneOf",
		"pattern": r"\bOneOf\s*\(",
		"required_macros": ["parserOneOf.pl"],
	},
	{
		"label": "NchooseK",
		"pattern": r"\bNchooseK\s*\(",
		"required_macros": ["PGchoicemacros.pl"],
	},
	{
		"label": "FormulaUpToConstant",
		"pattern": r"\bFormulaUpToConstant\s*\(",
		"required_macros": ["parserFormulaUpToConstant.pl"],
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
