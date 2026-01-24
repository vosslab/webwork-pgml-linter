# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_solution_hint_macros"
PLUGIN_NAME = "Legacy SOLUTION/HINT macros"
DEFAULT_ENABLED = True

# Pattern to match SOLUTION() and HINT() macro calls
SOLUTION_HINT_RX = re.compile(
	r'\b(SOLUTION|HINT)\s*\(',
	re.IGNORECASE
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when legacy SOLUTION() and HINT() macros are used.

	Old-style SOLUTION(EV3(<<'END')) and HINT() macros are deprecated.
	Modern PGML uses BEGIN_PGML_SOLUTION and BEGIN_PGML_HINT blocks.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stripped_text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find all SOLUTION() and HINT() macro calls
	for match in SOLUTION_HINT_RX.finditer(stripped_text):
		macro_name = match.group(1).upper()
		line = pgml_lint.parser.pos_to_line(newlines, match.start())

		if macro_name == "SOLUTION":
			message = (
				"SOLUTION() macro is deprecated legacy PG syntax; "
				"use BEGIN_PGML_SOLUTION...END_PGML_SOLUTION blocks instead"
			)
		else:  # HINT
			message = (
				"HINT() macro is deprecated legacy PG syntax; "
				"use BEGIN_PGML_HINT...END_PGML_HINT blocks instead"
			)

		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
