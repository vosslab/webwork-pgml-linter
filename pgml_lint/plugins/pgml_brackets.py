# Local modules
import pgml_lint.pgml


PLUGIN_ID = "pgml_brackets"
PLUGIN_NAME = "PGML bracket balance"
# Disabled by default: plain text brackets are common in PGML content
# (e.g., interval notation like (5,10] in documentation)
DEFAULT_ENABLED = False


#============================================


def _blank_spans(block_text: str, inline_spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
	"""
	Extract blank spans for bracket masking.

	Args:
		block_text: PGML block content.
		inline_spans: Inline spans to ignore.

	Returns:
		list[tuple[int, int]]: Blank spans.
	"""
	spans: list[tuple[int, int]] = []
	for match in pgml_lint.pgml.PGML_BLANK_RX.finditer(block_text):
		start = match.start()
		end = match.end()
		if any(span_start <= start < span_end for span_start, span_end in inline_spans):
			continue
		spans.append((start, end))
	return spans


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Check PGML bracket balance within PGML blocks.

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
	blank_spans_by_region = context.get("pgml_blank_spans", [])

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

		blank_spans: list[tuple[int, int]] = []
		if idx < len(blank_spans_by_region):
			blank_spans = blank_spans_by_region[idx]
		else:
			blank_spans = _blank_spans(block_text, inline_spans)

		bracket_issues = pgml_lint.pgml.check_pgml_bracket_balance(
			block_text,
			start,
			newlines,
			inline_spans,
			blank_spans,
		)
		issues.extend(bracket_issues)

	return issues
