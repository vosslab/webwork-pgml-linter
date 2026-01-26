# Standard Library
import re

PLUGIN_ID = "pgml_tex_color"
PLUGIN_NAME = "TeX color commands"
DEFAULT_ENABLED = True

COLOR_RX = re.compile(r"\\(?:textcolor|color)\b")


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on TeX color commands that do not render reliably in PGML.

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
		if COLOR_RX.search(line) is None:
			continue
		message = (
			"TeX color commands (\\color, \\textcolor) do not render reliably in "
			"PGML; use PGML tag wrappers or HTML spans instead"
		)
		issue = {"severity": "WARNING", "message": message, "line": line_num}
		issues.append(issue)

	return issues
