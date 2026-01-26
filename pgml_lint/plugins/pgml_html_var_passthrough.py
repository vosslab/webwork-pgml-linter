# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_html_var_passthrough"
PLUGIN_NAME = "HTML variables without PGML passthrough"
DEFAULT_ENABLED = True

HTML_ASSIGN_RX = re.compile(
	r"\$([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.=|=)\s*[^;]*<\s*"
	r"(span|div|sup|sub|br|p|a|img|style|table|tr|td|th)\b",
	re.IGNORECASE,
)


#============================================


def _find_html_vars(text: str) -> dict[str, int]:
	"""
	Find variables assigned HTML tags and track line numbers.
	"""
	vars_found: dict[str, int] = {}
	for line_num, line in enumerate(text.splitlines(), start=1):
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		match = HTML_ASSIGN_RX.search(clean)
		if match is None:
			continue
		name = match.group(1)
		if name not in vars_found:
			vars_found[name] = line_num
	return vars_found


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when HTML variables are output without PGML raw passthrough.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	vars_with_html = _find_html_vars(text)
	if not vars_with_html:
		return issues

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

	used_with_star: set[str] = set()
	used_without_star: set[str] = set()
	used_in_inline: set[str] = set()

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

		mask = [False] * len(region_text)
		for span_start, span_end in region_inline_spans:
			for idx in range(span_start, min(span_end, len(mask))):
				mask[idx] = True
			inline_text = region_text[span_start + 2 : span_end - 2]
			for name in vars_with_html:
				pattern = r"\$" + re.escape(name) + r"\b"
				if re.search(pattern, inline_text):
					used_in_inline.add(name)

		for name in vars_with_html:
			pattern = re.compile(r"\[\s*\$" + re.escape(name) + r"\s*\](\*)?")
			for match in pattern.finditer(region_text):
				if match.start() < len(mask) and mask[match.start()]:
					continue
				if match.group(1):
					used_with_star.add(name)
				else:
					used_without_star.add(name)

	for name, line in vars_with_html.items():
		if name in used_with_star or name in used_in_inline:
			continue
		if name not in used_without_star:
			continue
		pgml_ref = "[$" + name + "]*"
		message = (
			f"Variable ${name} contains HTML but is output without raw passthrough; "
			f"use {pgml_ref} to avoid escaping"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
