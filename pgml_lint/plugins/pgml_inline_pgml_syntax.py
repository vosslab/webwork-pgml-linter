# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_inline_pgml_syntax"
PLUGIN_NAME = "PGML syntax inside inline code"
DEFAULT_ENABLED = True

FORBIDDEN_SNIPPETS = [
	("[<", "PGML tag wrapper syntax found inside [@ @] block"),
	(">]{", "PGML tag wrapper syntax found inside [@ @] block"),
	("}{", "PGML tag wrapper syntax found inside [@ @] block"),
	("BEGIN_PGML", "Nested BEGIN_PGML found inside [@ @] block"),
	("END_PGML", "Nested END_PGML found inside [@ @] block"),
]


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when inline Perl blocks attempt to emit PGML structural syntax.

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

	inline_spans_by_region_obj = context.get("pgml_inline_spans", [])
	inline_spans_by_region = (
		list(inline_spans_by_region_obj)
		if isinstance(inline_spans_by_region_obj, list)
		else []
	)

	for region_idx, region in enumerate(pgml_block_regions):
		if not isinstance(region, dict):
			continue
		start = region.get("start")
		end = region.get("end")
		if not isinstance(start, int) or not isinstance(end, int):
			continue

		region_text = text[start:end]

		region_inline_spans: list[tuple[int, int]] = []
		if region_idx < len(inline_spans_by_region):
			spans_obj = inline_spans_by_region[region_idx]
			if isinstance(spans_obj, list):
				region_inline_spans = spans_obj
		else:
			inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
				region_text,
				start,
				newlines,
			)
			issues.extend(inline_issues)
			region_inline_spans = inline_spans

		for span_start, span_end in region_inline_spans:
			code_start = span_start + 2
			code_end = max(span_start + 2, span_end - 2)
			if code_start >= len(region_text):
				continue
			code = region_text[code_start:code_end]
			base_offset = start + code_start

			for snippet, message in FORBIDDEN_SNIPPETS:
				idx = code.find(snippet)
				if idx == -1:
					continue
				line = pgml_lint.parser.pos_to_line(newlines, base_offset + idx)
				issue = {"severity": "ERROR", "message": message, "line": line}
				issues.append(issue)

	return issues
