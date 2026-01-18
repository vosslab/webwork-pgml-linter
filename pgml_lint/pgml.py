# Standard Library
import re

# Local modules
import pgml_lint.parser


PGML_BLANK_RX = re.compile(r"\[[ \t]*_+[ \t]*\]")
PGML_INLINE_OPEN = "[@"
PGML_INLINE_CLOSE = "@]"
VAR_RX = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


#============================================


def extract_inline_spans(
	block_text: str,
	start_offset: int,
	newlines: list[int],
) -> tuple[list[dict[str, object]], list[tuple[int, int]]]:
	"""
	Extract PGML inline code spans and report unbalanced markers.

	Args:
		block_text: PGML block content.
		start_offset: Offset of the block within the full text.
		newlines: Newline index.

	Returns:
		tuple[list[dict[str, object]], list[tuple[int, int]]]: Issues and spans.
	"""
	issues: list[dict[str, object]] = []
	spans: list[tuple[int, int]] = []
	stack: list[int] = []

	i = 0
	while i < len(block_text) - 1:
		snippet = block_text[i : i + 2]
		if snippet == PGML_INLINE_OPEN:
			stack.append(i)
			i += 2
			continue
		if snippet == PGML_INLINE_CLOSE:
			if not stack:
				line = pgml_lint.parser.pos_to_line(newlines, start_offset + i)
				message = "PGML inline close @] without matching [@"
				issue = {"severity": "WARNING", "message": message, "line": line}
				issues.append(issue)
				i += 2
				continue
			start = stack.pop()
			spans.append((start, i + 2))
			i += 2
			continue
		i += 1

	for start in stack:
		line = pgml_lint.parser.pos_to_line(newlines, start_offset + start)
		message = "PGML inline open [@ without matching @]"
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues, spans


#============================================


def _extract_braced_payload(text: str, start: int) -> tuple[str, int, bool]:
	"""
	Extract a balanced { ... } payload starting at start.

	Args:
		text: Input text.
		start: Position of the opening brace.

	Returns:
		tuple[str, int, bool]: Payload, end position, and success flag.
	"""
	if start >= len(text) or text[start] != "{":
		payload = ""
		return payload, start, False

	depth = 0
	in_sq = False
	in_dq = False
	escape = False
	i = start
	while i < len(text):
		ch = text[i]
		if escape:
			escape = False
			i += 1
			continue
		if ch == "\\":
			escape = True
			i += 1
			continue
		if (not in_dq) and (ch == "'") and (not in_sq):
			in_sq = True
			i += 1
			continue
		if in_sq and ch == "'":
			in_sq = False
			i += 1
			continue
		if (not in_sq) and (ch == '"') and (not in_dq):
			in_dq = True
			i += 1
			continue
		if in_dq and ch == '"':
			in_dq = False
			i += 1
			continue

		if (not in_sq) and (not in_dq):
			if ch == "{":
				depth += 1
			elif ch == "}":
				depth -= 1
				if depth == 0:
					payload = text[start + 1 : i]
					end_pos = i + 1
					return payload, end_pos, True
		i += 1

	payload = ""
	return payload, start, False


#============================================


def scan_pgml_blanks(
	block_text: str,
	start_offset: int,
	newlines: list[int],
	inline_spans: list[tuple[int, int]],
) -> tuple[list[dict[str, object]], set[str], list[tuple[int, int]]]:
	"""
	Check PGML blanks for missing or malformed specs.

	Args:
		block_text: PGML block content.
		start_offset: Offset of the block within the full text.
		newlines: Newline index.
		inline_spans: Inline code spans to ignore.

	Returns:
		tuple[list[dict[str, object]], set[str], list[tuple[int, int]]]: Issues, variables, blank spans.
	"""
	issues: list[dict[str, object]] = []
	vars_found: set[str] = set()
	blank_spans: list[tuple[int, int]] = []

	for match in PGML_BLANK_RX.finditer(block_text):
		start = match.start()
		end = match.end()
		blank_spans.append((start, end))
		if any(span_start <= start < span_end for span_start, span_end in inline_spans):
			continue

		line = pgml_lint.parser.pos_to_line(newlines, start_offset + start)
		cursor = end
		while cursor < len(block_text) and block_text[cursor].isspace():
			cursor += 1

		is_star = False
		if cursor < len(block_text) and block_text[cursor] == "*":
			is_star = True
			cursor += 1
			while cursor < len(block_text) and block_text[cursor].isspace():
				cursor += 1

		if cursor >= len(block_text) or block_text[cursor] != "{":
			message = "PGML blank missing answer spec"
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)
			continue

		payload, end_pos, ok = _extract_braced_payload(block_text, cursor)
		if not ok:
			message = "PGML blank spec has unbalanced braces"
			issue = {"severity": "ERROR", "message": message, "line": line}
			issues.append(issue)
			continue

		if payload.strip() == "":
			message = "PGML blank spec is empty"
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

		for var_match in VAR_RX.finditer(payload):
			vars_found.add(var_match.group(1))

		trail = block_text[end_pos:]
		if is_star is False and re.match(r"\s*\*\s*\{", trail):
			message = "PGML blank uses both payload and star specs"
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

	return issues, vars_found, blank_spans


#============================================


def _extract_math_spans(block_text: str) -> list[tuple[int, int]]:
	"""
	Extract PGML math span positions to exclude from bracket checking.

	PGML math delimiters:
	- [`...`] for display math
	- [:...:] for inline math (with optional modifiers like :+)

	Args:
		block_text: PGML block content.

	Returns:
		list[tuple[int, int]]: Math span positions (start, end).
	"""
	spans: list[tuple[int, int]] = []
	i = 0
	while i < len(block_text) - 1:
		# Check for [`...`] display math
		if block_text[i:i+2] == "[`":
			start = i
			j = i + 2
			while j < len(block_text) - 1:
				if block_text[j:j+2] == "`]":
					spans.append((start, j + 2))
					i = j + 2
					break
				j += 1
			else:
				i += 1
			continue
		# Check for [:...:] inline math (handles modifiers like :+ :* etc)
		if block_text[i:i+2] == "[:":
			start = i
			j = i + 2
			while j < len(block_text) - 1:
				if block_text[j] == ":" and j + 1 < len(block_text) and block_text[j+1] == "]":
					spans.append((start, j + 2))
					i = j + 2
					break
				# Handle modifiers like :+] or :*]
				if block_text[j] == ":" and j + 2 < len(block_text) and block_text[j+2] == "]":
					spans.append((start, j + 3))
					i = j + 3
					break
				j += 1
			else:
				i += 1
			continue
		i += 1
	return spans


#============================================


def check_pgml_bracket_balance(
	block_text: str,
	start_offset: int,
	newlines: list[int],
	inline_spans: list[tuple[int, int]],
	blank_spans: list[tuple[int, int]],
) -> list[dict[str, object]]:
	"""
	Check for unbalanced PGML bracket usage, ignoring blanks, inline code, and math.

	Args:
		block_text: PGML block content.
		start_offset: Offset of the block within the full text.
		newlines: Newline index.
		inline_spans: Inline code spans.
		blank_spans: Blank marker spans.

	Returns:
		list[dict[str, object]]: Issue dicts.
	"""
	issues: list[dict[str, object]] = []
	# Extract math spans to exclude from bracket checking
	math_spans = _extract_math_spans(block_text)
	masked = list(block_text)
	for span_start, span_end in inline_spans + blank_spans + math_spans:
		for i in range(span_start, min(span_end, len(masked))):
			masked[i] = " "
	masked_text = "".join(masked)

	stack: list[int] = []
	i = 0
	while i < len(masked_text):
		ch = masked_text[i]
		if ch == "\\":
			i += 2
			continue
		if ch == "[":
			stack.append(i)
		elif ch == "]":
			if not stack:
				line = pgml_lint.parser.pos_to_line(newlines, start_offset + i)
				message = "PGML bracket close ] without matching ["
				issue = {"severity": "WARNING", "message": message, "line": line}
				issues.append(issue)
			else:
				stack.pop()
		i += 1

	for start in stack:
		line = pgml_lint.parser.pos_to_line(newlines, start_offset + start)
		message = "PGML bracket open [ without matching ]"
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	return issues
