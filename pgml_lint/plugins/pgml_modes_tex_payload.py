# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_modes_tex_payload"
PLUGIN_NAME = "MODES TeX payloads should be empty"
DEFAULT_ENABLED = True

MODES_RX = re.compile(r"\bMODES\s*\(")

DELIM_PAIRS = {
	"{": "}",
	"(": ")",
	"[": "]",
	"<": ">",
}


#============================================


def _extract_paren_payload(text: str, start: int) -> tuple[str, int] | None:
	"""
	Extract a balanced parenthesis payload starting at start.
	"""
	if start >= len(text) or text[start] != "(":
		return None
	depth = 0
	in_sq = False
	in_dq = False
	escape = False
	for i in range(start, len(text)):
		ch = text[i]
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
			depth += 1
			continue
		if ch == ")":
			depth -= 1
			if depth == 0:
				return text[start + 1 : i], i + 1
	return None


#============================================


def _parse_quoted(text: str, start: int) -> tuple[str, int] | None:
	"""
	Parse a quoted string starting at start.
	"""
	quote = text[start]
	if quote not in {"'", '"'}:
		return None
	escape = False
	for i in range(start + 1, len(text)):
		ch = text[i]
		if escape:
			escape = False
			continue
		if ch == "\\":
			escape = True
			continue
		if ch == quote:
			return text[start + 1 : i], i + 1
	return None


#============================================


def _parse_q_quoted(text: str, start: int) -> tuple[str, int] | None:
	"""
	Parse q/qq quoted strings starting at start.
	"""
	if text[start:start + 2] == "qq":
		tag_end = start + 2
	elif text[start:start + 1] == "q":
		tag_end = start + 1
	else:
		return None

	if tag_end >= len(text):
		return None
	delim = text[tag_end]
	close_delim = DELIM_PAIRS.get(delim, delim)
	i = tag_end + 1
	while i < len(text):
		ch = text[i]
		if ch == "\\":
			i += 2
			continue
		if ch == close_delim:
			return text[tag_end + 1 : i], i + 1
		i += 1
	return None


#============================================


def _find_tex_assignments(payload: str) -> list[tuple[int, bool]]:
	"""
	Return (offset, is_empty) for TeX => assignments in a MODES payload.
	"""
	assignments: list[tuple[int, bool]] = []
	in_sq = False
	in_dq = False
	escape = False
	i = 0
	while i < len(payload):
		ch = payload[i]
		if escape:
			escape = False
			i += 1
			continue
		if ch == "\\":
			escape = True
			i += 1
			continue
		if in_sq:
			if ch == "'":
				in_sq = False
			i += 1
			continue
		if in_dq:
			if ch == '"':
				in_dq = False
			i += 1
			continue
		if ch == "'":
			in_sq = True
			i += 1
			continue
		if ch == '"':
			in_dq = True
			i += 1
			continue

		if payload[i:i + 3] == "TeX":
			prev = payload[i - 1] if i > 0 else ""
			next_char = payload[i + 3] if i + 3 < len(payload) else ""
			if (prev.isalnum() or prev == "_") or (next_char.isalnum() or next_char == "_"):
				i += 1
				continue
			cursor = i + 3
			while cursor < len(payload) and payload[cursor].isspace():
				cursor += 1
			if payload[cursor:cursor + 2] != "=>":
				i += 1
				continue
			cursor += 2
			while cursor < len(payload) and payload[cursor].isspace():
				cursor += 1
			if cursor >= len(payload):
				assignments.append((i, True))
				i = cursor
				continue

			if payload[cursor] in {"'", '"'}:
				result = _parse_quoted(payload, cursor)
				if result is None:
					assignments.append((i, False))
					i = cursor + 1
					continue
				value, end_pos = result
				assignments.append((i, value.strip() == ""))
				i = end_pos
				continue

			if payload[cursor] == "q":
				result = _parse_q_quoted(payload, cursor)
				if result is not None:
					value, end_pos = result
					assignments.append((i, value.strip() == ""))
					i = end_pos
					continue

			assignments.append((i, False))
		i += 1

	return assignments


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when MODES() uses non-empty TeX payloads.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	newlines = pgml_lint.parser.build_newline_index(text)

	cursor = 0
	while True:
		match = MODES_RX.search(text, cursor)
		if match is None:
			break
		open_paren = match.end() - 1
		result = _extract_paren_payload(text, open_paren)
		if result is None:
			cursor = match.end()
			continue
		payload, end_pos = result
		payload_start = open_paren + 1
		for offset, is_empty in _find_tex_assignments(payload):
			if is_empty:
				continue
			line = pgml_lint.parser.pos_to_line(newlines, payload_start + offset)
			message = "MODES() TeX payload is non-empty; use TeX => '' for PGML output"
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)
		cursor = end_pos

	return issues
