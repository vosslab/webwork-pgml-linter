# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_tag_wrapper_tex"
PLUGIN_NAME = "PGML tag wrappers should avoid TeX payloads"
DEFAULT_ENABLED = True

TAG_WRAPPER_OPEN = "[<"
TAG_WRAPPER_CLOSE = ">]"

NON_EMPTY_PAYLOAD_RX = re.compile(r"[^\s,'\"]")


#============================================


def _extract_payloads(line: str, start: int) -> list[str] | None:
	"""
	Extract tag wrapper payloads from a single line.
	"""
	if line[start:start + 2] != TAG_WRAPPER_OPEN:
		return None
	label_end = line.find(TAG_WRAPPER_CLOSE, start + 2)
	if label_end == -1:
		return None
	cursor = label_end + 2
	payloads: list[str] = []
	while cursor < len(line):
		while cursor < len(line) and line[cursor].isspace():
			cursor += 1
		if cursor >= len(line) or line[cursor] != "{":
			break
		payload, end_pos, ok = pgml_lint.pgml._extract_braced_payload(line, cursor)
		if not ok:
			return None
		payloads.append(payload)
		cursor = end_pos
	if not payloads:
		return None
	return payloads


#============================================


def _payload_has_content(payload: str) -> bool:
	"""
	Return True when payload has non-empty content.
	"""
	return NON_EMPTY_PAYLOAD_RX.search(payload) is not None


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when PGML tag wrapper TeX payloads are non-empty.
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
	inline_spans_by_region: list[list[tuple[int, int]]] = []
	inline_spans_obj = context.get("pgml_inline_spans", [])
	if isinstance(inline_spans_obj, list):
		inline_spans_by_region = inline_spans_obj

	for region_idx, region in enumerate(pgml_block_regions):
		if not isinstance(region, dict):
			continue
		start = region.get("start")
		end = region.get("end")
		if not isinstance(start, int) or not isinstance(end, int):
			continue

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

		line_offset = 0
		for line in block_text.splitlines():
			search_start = 0
			while True:
				open_idx = line.find(TAG_WRAPPER_OPEN, search_start)
				if open_idx == -1:
					break
				abs_open = line_offset + open_idx
				if any(span_start <= abs_open < span_end for span_start, span_end in inline_spans):
					search_start = open_idx + 2
					continue
				payloads = _extract_payloads(line, open_idx)
				if payloads is None:
					search_start = open_idx + 2
					continue
				if len(payloads) >= 2 and _payload_has_content(payloads[1]):
					line_number = pgml_lint.parser.pos_to_line(newlines, start + abs_open)
					message = (
						"PGML tag wrapper has non-empty TeX payload; "
						"use an empty TeX payload unless needed"
					)
					issue = {"severity": "WARNING", "message": message, "line": line_number}
					issues.append(issue)
				search_start = open_idx + 2
			line_offset += len(line) + 1

	return issues
