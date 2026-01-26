# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_blob_payloads"
PLUGIN_NAME = "Embedded blob payloads"
DEFAULT_ENABLED = True

BASE64_RX = re.compile(r"[A-Za-z0-9+/]{800,}={0,2}")


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on likely embedded blob payloads.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	for match in BASE64_RX.finditer(text):
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = "Base64-like blob payload detected; consider removing embedded data"
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	line_num = 0
	for line in text.splitlines():
		line_num += 1
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		lower = clean.lower()
		if "ggbbase64" in lower:
			message = "ggbbase64 payload marker detected; avoid embedded applet blobs"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)
		if "base64" in lower and "=>" in clean:
			message = "base64 payload marker detected; avoid embedded blobs"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)

	return issues
