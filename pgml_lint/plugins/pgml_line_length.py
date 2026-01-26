# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_line_length"
PLUGIN_NAME = "Extreme line length"
DEFAULT_ENABLED = True

WARN_THRESHOLD = 200
ERROR_THRESHOLD = 400


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on extreme line lengths and blob-like lines.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))

	line_num = 0
	for line in text.splitlines():
		line_num += 1
		raw = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		length = len(raw)
		if length <= WARN_THRESHOLD:
			continue
		if length > ERROR_THRESHOLD:
			message = f"Line length {length} exceeds {ERROR_THRESHOLD} characters"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)
			if " " not in raw and "\t" not in raw:
				message = "Long line without whitespace suggests embedded blob payload"
				issue = {"severity": "WARNING", "message": message, "line": line_num}
				issues.append(issue)
			continue
		message = f"Line length {length} exceeds {WARN_THRESHOLD} characters"
		issue = {"severity": "WARNING", "message": message, "line": line_num}
		issues.append(issue)

	return issues
