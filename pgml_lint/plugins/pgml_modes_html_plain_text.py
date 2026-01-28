# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_modes_html_plain_text"
PLUGIN_NAME = "MODES HTML payloads without tags"
DEFAULT_ENABLED = True

MODES_RX = re.compile(r"\bMODES\s*\(")
HTML_TAG_RX = re.compile(r"<\s*/?\s*[a-zA-Z][^>]*>")

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

def _find_html_assignments(payload: str) -> list[tuple[int, str]]:
	"""
	Return (offset, value) for HTML => assignments with string payloads.
	"""
	assignments: list[tuple[int, str]] = []
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

		if payload[i:i + 4] == "HTML":
			prev = payload[i - 1] if i > 0 else ""
			next_char = payload[i + 4] if i + 4 < len(payload) else ""
			if (prev.isalnum() or prev == "_") or (next_char.isalnum() or next_char == "_"):
				i += 1
				continue
			cursor = i + 4
			while cursor < len(payload) and payload[cursor].isspace():
				cursor += 1
			if payload[cursor:cursor + 2] != "=>":
				i += 1
				continue
			cursor += 2
			while cursor < len(payload) and payload[cursor].isspace():
				cursor += 1
			if cursor >= len(payload):
				i = cursor
				continue

			if payload[cursor] in {"'", '"'}:
				result = _parse_quoted(payload, cursor)
				if result is None:
					i = cursor + 1
					continue
				value, end_pos = result
				assignments.append((i, value))
				i = end_pos
				continue

			if payload[cursor] == "q":
				result = _parse_q_quoted(payload, cursor)
				if result is not None:
					value, end_pos = result
					assignments.append((i, value))
					i = end_pos
					continue

		i += 1

	return assignments


#============================================


def _has_html_tags(text: str) -> bool:
	"""
	Return True when the string contains HTML tags.
	"""
	return HTML_TAG_RX.search(text) is not None


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when MODES() HTML payloads have no HTML tags.
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
		for offset, value in _find_html_assignments(payload):
			if _has_html_tags(value):
				continue
			line = pgml_lint.parser.pos_to_line(newlines, payload_start + offset)
			message = (
				"MODES() HTML payload has no HTML tags; replace with plain string instead "
				"of MODES()"
			)
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)
		cursor = end_pos

	return issues
