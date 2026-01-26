# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_span_interpolation"
PLUGIN_NAME = "PGML span interpolation"
DEFAULT_ENABLED = True

SPAN_ASSIGN_RX = re.compile(
	r"\$([A-Za-z_][A-Za-z0-9_]*)\s*(?:\.=|=)\s*[^;]*<\s*span\b",
	re.IGNORECASE,
)


#============================================


def _find_span_vars(text: str) -> dict[str, int]:
	"""
	Find variables assigned HTML spans and record line numbers.

	Args:
		text: Full file contents.

	Returns:
		dict[str, int]: Variable name -> line number.
	"""
	vars_found: dict[str, int] = {}
	line_num = 0
	for line in text.splitlines():
		line_num += 1
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		if not clean:
			continue
		match = SPAN_ASSIGN_RX.search(clean)
		if not match:
			continue
		name = match.group(1)
		if name not in vars_found:
			vars_found[name] = line_num
	return vars_found


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when span HTML variables are not interpolated with [$var] in PGML.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	vars_with_span = _find_span_vars(text)
	if not vars_with_span:
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

	found_vars: set[str] = set()

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
			for i in range(span_start, min(span_end, len(mask))):
				mask[i] = True

		for name in vars_with_span:
			if name in found_vars:
				continue
			pattern = re.compile(r"\[\s*\$" + re.escape(name) + r"\s*\]")
			for match in pattern.finditer(region_text):
				if match.start() < len(mask) and mask[match.start()]:
					continue
				found_vars.add(name)
				break

	for name, line in vars_with_span.items():
		if name in found_vars:
			continue
		pgml_ref = "[$" + name + "]"
		message = (
			f"Variable ${name} contains <span> HTML but is not interpolated with "
			f"{pgml_ref} in PGML; HTML may be escaped"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
