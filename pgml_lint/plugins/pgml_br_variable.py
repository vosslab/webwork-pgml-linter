# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_br_variable"
PLUGIN_NAME = "Legacy $BR variable"
DEFAULT_ENABLED = True

# Pattern to match $BR variable (not in strings)
BR_VAR_RX = re.compile(r'\$BR\b')


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when legacy $BR variable is used.

	$BR is old-style PG syntax for line breaks.
	Modern PGML uses blank lines for paragraph breaks.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stripped_text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find all $BR variable usages
	for match in BR_VAR_RX.finditer(stripped_text):
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = (
			"$BR is deprecated legacy PG syntax; "
			"use blank lines in PGML for paragraph breaks"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
