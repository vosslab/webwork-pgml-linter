# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_loadmacros_integrity"
PLUGIN_NAME = "loadMacros integrity checks"
DEFAULT_ENABLED = True

LOADMACROS_RX = re.compile(r"\bloadMacros\s*\(")
SMART_QUOTES_RX = re.compile(r"[\u2018\u2019\u201c\u201d]")
MISSING_COMMA_RX = re.compile(r"(['\"][^'\"]+['\"])\s+(['\"][^'\"]+['\"])")


#============================================


def _mask_strings(line: str) -> list[bool]:
	"""
	Return a mask indicating which positions are inside strings.
	"""
	mask = [False] * len(line)
	in_sq = False
	in_dq = False
	escape = False
	for idx, ch in enumerate(line):
		if escape:
			mask[idx] = True
			escape = False
			continue
		if ch == "\\":
			mask[idx] = True
			escape = True
			continue
		if in_sq:
			mask[idx] = True
			if ch == "'":
				in_sq = False
			continue
		if in_dq:
			mask[idx] = True
			if ch == '"':
				in_dq = False
			continue
		if ch == "'":
			mask[idx] = True
			in_sq = True
			continue
		if ch == '"':
			mask[idx] = True
			in_dq = True
			continue
	return mask


#============================================


def _find_loadmacros_open(line: str) -> int | None:
	"""
	Locate the '(' after loadMacros outside strings.
	"""
	mask = _mask_strings(line)
	for match in LOADMACROS_RX.finditer(line):
		if mask[match.start()]:
			continue
		return match.end() - 1
	return None


#============================================


def _scan_parens(line: str, start_idx: int, depth: int) -> tuple[int, int]:
	"""
	Scan a line and update paren depth, returning closing index if found.
	"""
	in_sq = False
	in_dq = False
	escape = False
	i = start_idx
	while i < len(line):
		ch = line[i]
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
		if ch == "(":
			depth += 1
			i += 1
			continue
		if ch == ")":
			depth -= 1
			if depth == 0:
				return depth, i
			i += 1
			continue
		i += 1
	return depth, -1


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Validate loadMacros(...) syntax and common pitfalls.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))

	lines = text.splitlines()
	in_load = False
	load_start_line = 0
	block_lines: list[str] = []
	depth = 0
	pending_semicolon_check = None

	for idx, line in enumerate(lines, start=1):
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)

		if pending_semicolon_check is not None:
			stripped = clean.strip()
			if stripped == "":
				continue
			if stripped.startswith(";"):
				pending_semicolon_check = None
				continue
			message = "loadMacros() missing trailing semicolon"
			issue = {
				"severity": "ERROR",
				"message": message,
				"line": pending_semicolon_check,
			}
			issues.append(issue)
			pending_semicolon_check = None

		if not in_load:
			open_idx = _find_loadmacros_open(clean)
			if open_idx is None:
				continue
			in_load = True
			load_start_line = idx
			block_lines = []
			depth = 1
			segment = clean[open_idx + 1 :]
			block_lines.append(segment)
			depth, close_idx = _scan_parens(clean, open_idx + 1, depth)
			if close_idx != -1:
				in_load = False
				block_lines[-1] = clean[open_idx + 1 : close_idx]
				remainder = clean[close_idx + 1 :]
				if ";" not in remainder:
					pending_semicolon_check = idx
				block_text = "\n".join(block_lines)
				if SMART_QUOTES_RX.search(block_text):
					message = "loadMacros() contains smart quotes"
					issue = {"severity": "ERROR", "message": message, "line": idx}
					issues.append(issue)
				trimmed = block_text.strip()
				if trimmed == "":
					message = "loadMacros() has an empty macro list"
					issue = {"severity": "ERROR", "message": message, "line": idx}
					issues.append(issue)
				if trimmed.endswith(","):
					message = "loadMacros() macro list ends with a trailing comma"
					issue = {"severity": "WARNING", "message": message, "line": idx}
					issues.append(issue)
				if MISSING_COMMA_RX.search(block_text):
					message = "loadMacros() entries appear to be missing a comma"
					issue = {"severity": "ERROR", "message": message, "line": idx}
					issues.append(issue)
			continue

		block_lines.append(clean)
		depth, close_idx = _scan_parens(clean, 0, depth)
		if close_idx == -1:
			continue
		in_load = False
		block_lines[-1] = clean[:close_idx]
		remainder = clean[close_idx + 1 :]
		if ";" not in remainder:
			pending_semicolon_check = idx
		block_text = "\n".join(block_lines)
		if SMART_QUOTES_RX.search(block_text):
			message = "loadMacros() contains smart quotes"
			issue = {"severity": "ERROR", "message": message, "line": idx}
			issues.append(issue)
		trimmed = block_text.strip()
		if trimmed == "":
			message = "loadMacros() has an empty macro list"
			issue = {"severity": "ERROR", "message": message, "line": idx}
			issues.append(issue)
		if trimmed.endswith(","):
			message = "loadMacros() macro list ends with a trailing comma"
			issue = {"severity": "WARNING", "message": message, "line": idx}
			issues.append(issue)
		if MISSING_COMMA_RX.search(block_text):
			message = "loadMacros() entries appear to be missing a comma"
			issue = {"severity": "ERROR", "message": message, "line": idx}
			issues.append(issue)

	if in_load:
		message = "loadMacros() missing closing parenthesis"
		issue = {"severity": "ERROR", "message": message, "line": load_start_line}
		issues.append(issue)

	return issues
