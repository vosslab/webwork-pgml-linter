# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_label_dot"
PLUGIN_NAME = "PGML label dot list trap"
DEFAULT_ENABLED = True

LABEL_DOT_RX = re.compile(
	r"chr\s*\(\s*65\s*\+\s*\$[A-Za-z_][A-Za-z0-9_]*\s*\)\s*\.\s*(['\"])"
	r"\.\s*\1"
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when labels are built as A. which can trigger list parsing.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))

	line_num = 0
	for line in text.splitlines():
		line_num += 1
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		if not clean:
			continue
		if LABEL_DOT_RX.search(clean):
			message = (
				"Label built as A. (chr(65 + $i) . '. ') can trigger PGML list parsing; "
				"use '*A.*' or 'A)' instead"
			)
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)

	return issues
