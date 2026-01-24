# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_ans_rule"
PLUGIN_NAME = "Legacy ans_rule() function"
DEFAULT_ENABLED = True

# Pattern to match ans_rule() and related functions
ANS_RULE_RX = re.compile(r'\bans_rule\s*\(')


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when legacy ans_rule() function is used.

	ans_rule() is old-style PG syntax for creating answer blanks.
	Modern PGML uses inline answer specs: [_]{$answer}

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stripped_text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find all ans_rule() calls
	for match in ANS_RULE_RX.finditer(stripped_text):
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = (
			"ans_rule() is deprecated legacy PG syntax; "
			"use PGML inline answer blanks like [_]{$answer} instead"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
