# Standard Library
import re

# Local modules
import pgml_lint.parser


PLUGIN_ID = "document_pairs"
PLUGIN_NAME = "DOCUMENT/ENDDOCUMENT pairing"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Check DOCUMENT()/ENDDOCUMENT() pairing.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	newlines = context.get("newlines", [])

	starts = [m.start() for m in re.finditer(r"\bDOCUMENT\s*\(\s*\)", text)]
	ends = [m.start() for m in re.finditer(r"\bENDDOCUMENT\s*\(\s*\)", text)]

	if not starts and not ends:
		return issues

	if len(starts) == 0 or len(ends) == 0:
		if starts:
			line = pgml_lint.parser.pos_to_line(newlines, starts[0])
			message = "DOCUMENT() present without ENDDOCUMENT()"
		else:
			line = pgml_lint.parser.pos_to_line(newlines, ends[0])
			message = "ENDDOCUMENT() present without DOCUMENT()"
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)
		return issues

	if len(starts) != len(ends):
		message = f"DOCUMENT() count does not match ENDDOCUMENT() (start={len(starts)}, end={len(ends)})"
		issue = {"severity": "ERROR", "message": message}
		issues.append(issue)
		return issues

	if starts and ends and ends[0] < starts[0]:
		line = pgml_lint.parser.pos_to_line(newlines, ends[0])
		message = "ENDDOCUMENT() appears before DOCUMENT()"
		issue = {"severity": "ERROR", "message": message, "line": line}
		issues.append(issue)

	return issues
