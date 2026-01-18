# Local modules
import pgml_lint.pgml


PLUGIN_ID = "pgml_blanks"
PLUGIN_NAME = "PGML blank specs"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Check PGML blank specs and capture referenced variables.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	regions = context.get("pgml_regions", [])
	text = str(context.get("text", ""))
	newlines = context.get("newlines", [])
	inline_spans_by_region = context.get("pgml_inline_spans", [])

	blank_vars: set[str] = set()
	blank_spans_by_region: list[list[tuple[int, int]]] = []

	for idx, region in enumerate(regions):
		start = int(region.get("start", 0))
		end = int(region.get("end", 0))
		block_text = text[start:end]

		inline_spans: list[tuple[int, int]] = []
		if idx < len(inline_spans_by_region):
			inline_spans = inline_spans_by_region[idx]
		else:
			inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
				block_text,
				start,
				newlines,
			)
			issues.extend(inline_issues)

		blank_issues, vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
			block_text,
			start,
			newlines,
			inline_spans,
		)
		issues.extend(blank_issues)
		blank_vars.update(vars_found)
		blank_spans_by_region.append(blank_spans)

	context["pgml_blank_vars"] = blank_vars
	context["pgml_blank_spans"] = blank_spans_by_region
	return issues
