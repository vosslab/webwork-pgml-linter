# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_modes_in_inline"
PLUGIN_NAME = "MODES inside inline eval blocks"
DEFAULT_ENABLED = True

MODES_RX = re.compile(r"\bMODES\s*\(")


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when MODES() appears inside [@ @] inline blocks.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []
	regions = context.get("pgml_regions", [])

	inline_spans_by_region: list[list[tuple[int, int]]] = []
	inline_spans_obj = context.get("pgml_inline_spans", [])
	if isinstance(inline_spans_obj, list):
		inline_spans_by_region = inline_spans_obj

	for region_idx, region in enumerate(regions):
		start = int(region.get("start", 0))
		end = int(region.get("end", 0))
		block_text = text[start:end]

		inline_spans: list[tuple[int, int]] = []
		if region_idx < len(inline_spans_by_region):
			inline_spans = inline_spans_by_region[region_idx]
		else:
			inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
				block_text,
				start,
				newlines,
			)
			issues.extend(inline_issues)

		for span_start, span_end in inline_spans:
			inline_text = block_text[span_start + 2 : span_end - 2]
			if MODES_RX.search(inline_text) is None:
				continue
			line = pgml_lint.parser.pos_to_line(newlines, start + span_start)
			message = (
				"MODES() used inside [@ @] block; MODES returns 1 in eval context and "
				"will not emit HTML"
			)
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

	return issues
