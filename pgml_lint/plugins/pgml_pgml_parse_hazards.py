# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml

PLUGIN_ID = "pgml_pgml_parse_hazards"
PLUGIN_NAME = "PGML parse hazards"
DEFAULT_ENABLED = True

UNSUPPORTED_BLOCKS = {"balance"}
BLOCK_TOKEN_RX = re.compile(r"^\s*\[\s*([A-Za-z]+)\s*\]\s*$")


#============================================


def _paren_balance(text: str) -> int:
	"""
	Return paren balance count (0 means balanced).
	"""
	in_sq = False
	in_dq = False
	escape = False
	balance = 0
	for ch in text:
		if escape:
			escape = False
			continue
		if ch == "\\":
			escape = True
			continue
		if in_sq:
			if ch == "'":
				in_sq = False
			continue
		if in_dq:
			if ch == '"':
				in_dq = False
			continue
		if ch == "'":
			in_sq = True
			continue
		if ch == '"':
			in_dq = True
			continue
		if ch == "(":
			balance += 1
		elif ch == ")":
			balance -= 1
	return balance


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on common PGML parse hazards.
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

		line_offset = 0
		for line in block_text.splitlines():
			match = BLOCK_TOKEN_RX.match(line)
			if match is None:
				line_offset += len(line) + 1
				continue
			token = match.group(1).lower()
			if token not in UNSUPPORTED_BLOCKS:
				line_offset += len(line) + 1
				continue
			line_number = pgml_lint.parser.pos_to_line(newlines, start + line_offset)
			message = f"Unknown PGML block token [{token}] may cause parser errors"
			issue = {"severity": "WARNING", "message": message, "line": line_number}
			issues.append(issue)
			line_offset += len(line) + 1

		for span_start, span_end in inline_spans:
			inline_text = block_text[span_start + 2 : span_end - 2]
			balance = _paren_balance(inline_text)
			if balance == 0:
				continue
			line_number = pgml_lint.parser.pos_to_line(newlines, start + span_start)
			message = "PGML inline code has unbalanced parentheses"
			issue = {"severity": "WARNING", "message": message, "line": line_number}
			issues.append(issue)

	return issues
