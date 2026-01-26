# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_html_in_text"
PLUGIN_NAME = "Raw HTML in PGML text"
DEFAULT_ENABLED = True

# HTML tags that are problematic in PGML text
PROBLEMATIC_TAGS = {
	'strong': 'use *bold* for bold text',
	'b': 'use *bold* for bold text',
	'i': 'use _italic_ for italic text',
	'em': 'use _italic_ for italic text',
	'u': 'use PGML markup or CSS classes',
	'sub': 'use LaTeX subscripts like [` x_2 `] for math',
	'sup': 'use LaTeX superscripts like [` x^2 `] for math',
	'br': 'use blank lines in PGML for line breaks',
	'p': 'use blank lines in PGML for paragraphs',
	'h1': 'use PGML headings',
	'h2': 'use PGML headings',
	'h3': 'use PGML headings',
	'h4': 'use PGML headings',
	'ul': 'use PGML list syntax',
	'ol': 'use PGML list syntax',
	'li': 'use PGML list syntax',
	'font': 'use CSS or PGML markup',
	'center': 'use PGML alignment syntax',
	'a': 'use PGML link syntax',
	'span': 'use PGML tag wrappers or MODES(HTML => ...) with [$var]',
	'style': 'move styles to HEADER_TEXT or CSS files',
}

# HTML entities that commonly cause issues
HTML_ENTITY_RX = re.compile(r'&(?:[a-zA-Z]+|#\d+|#x[0-9a-fA-F]+);')
TEX2JAX_CLASS_RX = re.compile(r'class\s*=\s*["\'][^"\']*\btex2jax_ignore\b[^"\']*["\']')


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when raw HTML tags or entities appear in PGML text.

	Raw HTML in PGML blocks gets stripped or mangled. Authors should use
	PGML markup instead (*, _, LaTeX, etc.).

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []

	# Get PGML regions (BEGIN_PGML...END_PGML blocks)
	pgml_block_regions_obj = context.get("pgml_block_regions", [])
	pgml_block_regions = (
		list(pgml_block_regions_obj)
		if isinstance(pgml_block_regions_obj, list)
		else []
	)

	# Get inline code spans to exclude them (HTML is allowed in [@ @]*)
	# pgml_inline_spans is a list of lists (one per region)
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
		# Note: spans are relative to region_text, not absolute positions
		mask = [False] * len(region_text)
		for span in region_inline_spans:
			if not isinstance(span, tuple) or len(span) != 2:
				continue
			span_start, span_end = span

			# Spans are already relative to the region
			for i in range(span_start, min(span_end, len(mask))):
				mask[i] = True

		# Check for problematic HTML tags (opening tags only, not closing tags)
		# Match <tag> or <tag attr="val"> but not </tag>
		tag_rx = re.compile(r'<([a-zA-Z]\w*)(?:\s[^>]*)?>|</([a-zA-Z]\w*)>')
		for match in tag_rx.finditer(region_text):
			# Skip if inside inline code span
			if match.start() < len(mask) and mask[match.start()]:
				continue

			# Only check opening tags (group 1), not closing tags (group 2)
			if match.group(2):
				continue

			tag_name = match.group(1).lower()
			if tag_name in PROBLEMATIC_TAGS:
				line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
				suggestion = PROBLEMATIC_TAGS[tag_name]
				message = (
					f"Raw HTML <{tag_name}> tag in PGML text will be stripped or mangled; "
					f"{suggestion}"
				)
				issue = {"severity": "WARNING", "message": message, "line": line}
				issues.append(issue)

		# Check for HTML entities
		for match in HTML_ENTITY_RX.finditer(region_text):
			# Skip if inside inline code span
			if match.start() < len(mask) and mask[match.start()]:
				continue

			entity = match.group(0)
			line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
			message = (
				f"HTML entity '{entity}' in PGML text may be mangled; "
				f"use Unicode characters or LaTeX instead"
			)
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

		# Check for tex2jax_ignore class usage
		for match in TEX2JAX_CLASS_RX.finditer(region_text):
			# Skip if inside inline code span
			if match.start() < len(mask) and mask[match.start()]:
				continue

			line = pgml_lint.parser.pos_to_line(newlines, start + match.start())
			message = (
				"HTML class \"tex2jax_ignore\" found in PGML text; "
				"this suppresses MathJax and often indicates rendering problems"
			)
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

	return issues
