# Standard Library
import re

PLUGIN_ID = "pgml_mojibake"
PLUGIN_NAME = "Mojibake/encoding glitches"
DEFAULT_ENABLED = True

MOJIBAKE_RX = re.compile(
	r"(\u00c2|\u00c3|\u00c2[\u0080-\u00bf]|\u00c3[\u0080-\u00bf]|"
	r"\u00e2[\u0080-\u009f]|\u00e2\u0080\u0099|\u00e2\u0080\u0093|"
	r"\u00e2\u0080\u0094|\u00e2\u0080\u00a2|\ufffd)"
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on common mojibake sequences that signal encoding issues.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stripped_text = str(context.get("stripped_text", ""))

	line_num = 0
	for line in stripped_text.splitlines():
		line_num += 1
		match = MOJIBAKE_RX.search(line)
		if match is None:
			continue
		token = ascii(match.group(0))
		message = (
			f"Possible mojibake sequence {token} detected; check for UTF-8/Latin-1 "
			"encoding mixups"
		)
		issue = {"severity": "WARNING", "message": message, "line": line_num}
		issues.append(issue)

	return issues
