# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_modes_html_escape"
PLUGIN_NAME = "MODES HTML escaped in PGML"
DEFAULT_ENABLED = True

# Pattern to match MODES() calls that produce HTML
# MODES(TeX => '...', HTML => '...')
MODES_RX = re.compile(
	r'\bMODES\s*\([^)]*HTML\s*=>\s*["\']([^"\']*<[^"\']*)["\']',
	re.DOTALL
)

# Pattern to match variable assignment from MODES()
# $var = MODES(...)
VAR_ASSIGN_MODES_RX = re.compile(
	r'\$([A-Za-z_][A-Za-z0-9_]*)\s*=\s*MODES\s*\([^)]*HTML\s*=>',
	re.DOTALL
)

# Pattern to match PGML interpolation [$var] but not [@ $var @]*
# This is tricky because we need to exclude [@...@]* blocks
PGML_INTERP_RX = re.compile(r'\[\$([A-Za-z_][A-Za-z0-9_]*)\]')


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when variables containing HTML from MODES() are interpolated in PGML.

	PGML escapes raw HTML in [$var] interpolation. Variables assigned from
	MODES(HTML => '<span>...', ...) should use [@ $var @]* instead.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	stripped_text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Find variables assigned from MODES() with HTML content
	html_vars: set[str] = set()
	for match in VAR_ASSIGN_MODES_RX.finditer(stripped_text):
		var_name = match.group(1)
		html_vars.add(var_name)

	# If no HTML-producing MODES() calls found, nothing to check
	if not html_vars:
		return issues

	# Get PGML regions (BEGIN_PGML...END_PGML blocks)
	pgml_block_regions_obj = context.get("pgml_block_regions", [])
	pgml_block_regions = (
		list(pgml_block_regions_obj)
		if isinstance(pgml_block_regions_obj, list)
		else []
	)

	# Get inline code spans to exclude them ([@ @]* blocks are OK)
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

		# Get inline spans for this specific region
		region_inline_spans: list[tuple[int, int]] = []
		if region_idx < len(inline_spans_by_region):
			spans_obj = inline_spans_by_region[region_idx]
			if isinstance(spans_obj, list):
				region_inline_spans = spans_obj

		# Build a mask for inline code spans within this region
		# Don't warn about [$var] inside [@ @]* blocks
		mask = [False] * len(region_text)
		for span in region_inline_spans:
			if not isinstance(span, tuple) or len(span) != 2:
				continue
			span_start, span_end = span

			# Spans are already relative to the region
			for i in range(span_start, min(span_end, len(mask))):
				mask[i] = True

		# Find [$var] interpolations in this region
		for match in PGML_INTERP_RX.finditer(region_text):
			# Skip if inside inline code span ([@ @]*)
			if match.start() < len(mask) and mask[match.start()]:
				continue

			var_name = match.group(1)
			if var_name in html_vars:
				line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
				message = (
					f"Variable ${var_name} contains HTML from MODES() but is used "
					f"in [$var] interpolation which escapes HTML; "
					f"use [@ ${var_name} @]* instead to render HTML"
				)
				issue = {"severity": "WARNING", "message": message, "line": line}
				issues.append(issue)

	return issues
