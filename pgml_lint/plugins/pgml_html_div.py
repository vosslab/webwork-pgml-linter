# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_html_div"
PLUGIN_NAME = "HTML div tags in PGML"
DEFAULT_ENABLED = True

DIV_TAG_RX = re.compile(r"<\s*/?\s*div\b", re.IGNORECASE)
ESCAPED_DIV_RX = re.compile(r"&lt;\s*/?\s*div\b", re.IGNORECASE)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when <div> tags appear in PGML blocks, even inside inline code.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	pgml_block_regions_obj = context.get("pgml_block_regions", [])
	pgml_block_regions = (
		list(pgml_block_regions_obj)
		if isinstance(pgml_block_regions_obj, list)
		else []
	)

	for region in pgml_block_regions:
		if not isinstance(region, dict):
			continue
		start = region.get("start")
		end = region.get("end")
		if not isinstance(start, int) or not isinstance(end, int):
			continue

		region_text = text[start:end]

		for match in DIV_TAG_RX.finditer(region_text):
			line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
			message = (
				"HTML <div> tag found in PGML content; "
				"avoid HTML divs because they often render incorrectly"
			)
			issue = {"severity": "ERROR", "message": message, "line": line}
			issues.append(issue)

		for match in ESCAPED_DIV_RX.finditer(region_text):
			line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
			message = (
				"Escaped HTML <div> tag found in PGML output; "
				"this indicates HTML is being escaped instead of rendered"
			)
			issue = {"severity": "ERROR", "message": message, "line": line}
			issues.append(issue)

	return issues
