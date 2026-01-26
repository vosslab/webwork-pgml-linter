# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_html_forbidden_tags"
PLUGIN_NAME = "Forbidden HTML tags in PGML"
DEFAULT_ENABLED = True

FORBIDDEN_TAGS = {
	"table": "use DataTable() or LayoutTable() from niceTables.pl",
	"tr": "use DataTable() or LayoutTable() from niceTables.pl",
	"td": "use DataTable() or LayoutTable() from niceTables.pl",
	"th": "use DataTable() or LayoutTable() from niceTables.pl",
	"thead": "use DataTable() or LayoutTable() from niceTables.pl",
	"tbody": "use DataTable() or LayoutTable() from niceTables.pl",
	"tfoot": "use DataTable() or LayoutTable() from niceTables.pl",
	"colgroup": "use DataTable() or LayoutTable() from niceTables.pl",
	"col": "use DataTable() or LayoutTable() from niceTables.pl",
}

TAG_RX = re.compile(
	r"<\s*/?\s*(" + "|".join(FORBIDDEN_TAGS.keys()) + r")\b",
	re.IGNORECASE,
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Error on forbidden HTML table-related tags inside PGML blocks.

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
		for match in TAG_RX.finditer(region_text):
			tag = match.group(1).lower()
			suggestion = FORBIDDEN_TAGS.get(tag, "use PGML-friendly markup")
			line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
			message = (
				f"HTML <{tag}> tag found in PGML content; {suggestion}"
			)
			issue = {"severity": "ERROR", "message": message, "line": line}
			issues.append(issue)

	return issues
