# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_old_answer_checkers"
PLUGIN_NAME = "Legacy answer checker functions"
DEFAULT_ENABLED = True

# Pattern to match old answer checker functions
OLD_CHECKERS_RX = re.compile(
	r'\b(num_cmp|str_cmp|fun_cmp|std_num_cmp|std_str_cmp|std_fun_cmp|'
	r'std_num_str_cmp|strict_num_cmp|strict_str_cmp)\s*\('
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when legacy answer checker functions are used.

	Old answer checkers like num_cmp(), str_cmp(), fun_cmp() are deprecated.
	Modern PG uses MathObjects with ->cmp() method.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stripped_text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find all old answer checker calls
	for match in OLD_CHECKERS_RX.finditer(stripped_text):
		checker_name = match.group(1)
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = (
			f"{checker_name}() is deprecated legacy PG syntax; "
			f"use MathObjects with ->cmp() method instead (e.g., $answer->cmp())"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
