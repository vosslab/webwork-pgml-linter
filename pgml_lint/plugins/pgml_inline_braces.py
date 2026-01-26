# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_inline_braces"
PLUGIN_NAME = "PGML inline brace balance"
DEFAULT_ENABLED = True


#============================================


def _scan_inline_braces(
	code: str,
	base_offset: int,
	newlines: list[int],
) -> list[dict[str, object]]:
	"""
	Check inline Perl code for unbalanced braces.

	Args:
		code: Inline code (without [@ @] markers).
		base_offset: Absolute offset for the first character in code.
		newlines: Newline index.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	stack: list[int] = []
	in_sq = False
	in_dq = False
	escape = False
	i = 0
	while i < len(code):
		ch = code[i]
		if in_sq or in_dq:
			if escape:
				escape = False
				i += 1
				continue
			if ch == "\\":
				escape = True
				i += 1
				continue
			if in_sq and ch == "'":
				in_sq = False
				i += 1
				continue
			if in_dq and ch == '"':
				in_dq = False
				i += 1
				continue
			i += 1
			continue

		if ch == "#":
			line_end = code.find("\n", i)
			if line_end == -1:
				return issues
			i = line_end + 1
			continue
		if ch == "'":
			in_sq = True
			i += 1
			continue
		if ch == '"':
			in_dq = True
			i += 1
			continue
		if ch == "{":
			stack.append(base_offset + i)
			i += 1
			continue
		if ch == "}":
			if not stack:
				line = pgml_lint.parser.pos_to_line(newlines, base_offset + i)
				message = "PGML inline code has unbalanced '}' brace"
				issue = {"severity": "ERROR", "message": message, "line": line}
				issues.append(issue)
				return issues
			stack.pop()
			i += 1
			continue
		i += 1

	if stack:
		pos = stack[-1]
		line = pgml_lint.parser.pos_to_line(newlines, pos)
		message = "PGML inline code has unclosed '{' brace"
		issue = {"severity": "ERROR", "message": message, "line": line}
		issues.append(issue)

	return issues


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when inline PGML Perl blocks have unbalanced braces.

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
			issues.extend(_scan_inline_braces(code, base_offset, newlines))

	return issues
