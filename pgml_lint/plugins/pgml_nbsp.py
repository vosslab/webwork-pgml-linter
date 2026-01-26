# Standard Library
import re

PLUGIN_ID = "pgml_nbsp"
PLUGIN_NAME = "Non-breaking spaces"
DEFAULT_ENABLED = True

NBSP_RX = re.compile(r"\u00a0|\u202f")


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on Unicode non-breaking spaces in PG files.

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
		if NBSP_RX.search(line) is None:
			continue
		message = (
			"Non-breaking space detected; replace with a normal space to avoid "
			"layout surprises"
		)
		issue = {"severity": "WARNING", "message": message, "line": line_num}
		issues.append(issue)

	return issues
