# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_underscore_emphasis"
PLUGIN_NAME = "PGML underscore emphasis balance"
DEFAULT_ENABLED = True


#============================================


def _is_word_char(ch: str) -> bool:
	"""
	Check if a character counts as a word character.

	Args:
		ch: Single character.

	Returns:
		bool: True if alphanumeric or underscore.
	"""
	return ch.isalnum() or ch == "_"


#============================================


def _masked_positions(
	region_text: str,
	inline_spans: list[tuple[int, int]],
	blank_spans: list[tuple[int, int]],
) -> list[bool]:
	"""
	Build a mask for positions to ignore.

	Args:
		region_text: PGML block text.
		inline_spans: Inline code spans.
		blank_spans: PGML blank spans.

	Returns:
		list[bool]: Mask list.
	"""
	mask = [False] * len(region_text)

	for span_start, span_end in inline_spans + blank_spans:
		for i in range(span_start, min(span_end, len(mask))):
			mask[i] = True

	for span_start, span_end in pgml_lint.pgml._extract_math_spans(region_text):
		for i in range(span_start, min(span_end, len(mask))):
			mask[i] = True

	return mask


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when underscore emphasis markers are unbalanced in PGML text.

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

	blank_spans_by_region_obj = context.get("pgml_blank_spans", [])
	blank_spans_by_region = (
		list(blank_spans_by_region_obj)
		if isinstance(blank_spans_by_region_obj, list)
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

		region_blank_spans: list[tuple[int, int]] = []
		if region_idx < len(blank_spans_by_region):
			spans_obj = blank_spans_by_region[region_idx]
			if isinstance(spans_obj, list):
				region_blank_spans = spans_obj
		else:
			blank_issues, _vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
				region_text,
				start,
				newlines,
				region_inline_spans,
			)
			issues.extend(blank_issues)
			region_blank_spans = blank_spans

		mask = _masked_positions(region_text, region_inline_spans, region_blank_spans)

		paragraph_positions: list[int] = []
		pos = 0
		for line in region_text.splitlines(keepends=True):
			if line.strip() == "":
				if len(paragraph_positions) % 2 == 1:
					open_pos = paragraph_positions[-1]
					line_num = pgml_lint.parser.pos_to_line(newlines, start + open_pos)
					message = "PGML underscore emphasis not closed before paragraph ends"
					issue = {"severity": "WARNING", "message": message, "line": line_num}
					issues.append(issue)
				paragraph_positions = []
				pos += len(line)
				continue

			for idx, ch in enumerate(line):
				if ch != "_":
					continue
				abs_pos = pos + idx
				if abs_pos < len(mask) and mask[abs_pos]:
					continue
				if idx > 0 and line[idx - 1] == "\\":
					continue
				prev_ch = line[idx - 1] if idx > 0 else ""
				next_ch = line[idx + 1] if idx + 1 < len(line) else ""
				if prev_ch and next_ch and _is_word_char(prev_ch) and _is_word_char(next_ch):
					continue
				paragraph_positions.append(abs_pos)

			pos += len(line)

		if len(paragraph_positions) % 2 == 1:
			open_pos = paragraph_positions[-1]
			line_num = pgml_lint.parser.pos_to_line(newlines, start + open_pos)
			message = "PGML underscore emphasis not closed before paragraph ends"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)

	return issues
