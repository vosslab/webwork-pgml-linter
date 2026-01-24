# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_text_blocks"
PLUGIN_NAME = "Deprecated TEXT blocks"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when deprecated BEGIN_TEXT/END_TEXT blocks are used.

	Modern PGML files should use BEGIN_PGML/END_PGML instead.
	TEXT blocks are legacy PG syntax and should be migrated to PGML.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find all BEGIN_TEXT markers
	text_block_rx = re.compile(r"(?m)^[ \t]*BEGIN_TEXT\b")
	for match in text_block_rx.finditer(text):
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = (
			"BEGIN_TEXT is deprecated legacy PG syntax; "
			"use BEGIN_PGML with PGML.pl for modern WebWork problems"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
