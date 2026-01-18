# Local modules
import pgml_lint.pgml


PLUGIN_ID = "pgml_inline"
PLUGIN_NAME = "PGML inline markers"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Check PGML inline marker pairs.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	regions = context.get("pgml_regions", [])
	text = str(context.get("text", ""))
	newlines = context.get("newlines", [])

	inline_spans_by_region: list[list[tuple[int, int]]] = []
	for region in regions:
		start = int(region.get("start", 0))
		end = int(region.get("end", 0))
		block_text = text[start:end]
		inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
			block_text,
			start,
			newlines,
		)
		issues.extend(inline_issues)
		inline_spans_by_region.append(inline_spans)

	context["pgml_inline_spans"] = inline_spans_by_region
	return issues
