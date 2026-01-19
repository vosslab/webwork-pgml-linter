# Standard Library
import bisect
import os
import re


BLOCK_MARKER_RX = re.compile(
	r"(?m)^[ \t]*(BEGIN|END)_(PGML(?:_(SOLUTION|HINT))?|TEXT|SOLUTION|HINT)\b",
)

FILENAME_RX = re.compile(r"""['\"]([^'\"]+\.(?:pl|pg))['\"]""")
# Match scalar declarations: my $var, our $var
VAR_DECL_RX = re.compile(r"\b(?:my|our)\s+\$([A-Za-z_][A-Za-z0-9_]*)")
# Match scalar assignments: $var =
VAR_ASSIGN_RX = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)\s*=")
# Match array/hash declarations: my @arr, my %hash, our @arr, our %hash
ARRAY_HASH_DECL_RX = re.compile(r"\b(?:my|our)\s+[@%]([A-Za-z_][A-Za-z0-9_]*)")
# Match array/hash assignments: @arr =, %hash =
ARRAY_HASH_ASSIGN_RX = re.compile(r"[@%]([A-Za-z_][A-Za-z0-9_]*)\s*=")
# Match list assignments: ($var1, $var2, ...) =
LIST_ASSIGN_RX = re.compile(r"\(\s*(?:\$([A-Za-z_][A-Za-z0-9_]*)\s*,?\s*)+\s*\)\s*=")
# Match individual variables in list context
LIST_VAR_RX = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")
# Match array element assignments: $arr[...] = (creates @arr via autovivification)
ARRAY_ELEM_ASSIGN_RX = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)\s*\[[^\]]+\]\s*=")
# Match hash element assignments: $hash{...} = (creates %hash via autovivification)
HASH_ELEM_ASSIGN_RX = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)\s*\{[^\}]+\}\s*=")

MACRO_CALL_NAMES = {"loadMacros", "includePGproblem"}


#============================================


def build_newline_index(text: str) -> list[int]:
	"""
	Return sorted positions of "\n" characters.

	Args:
		text: Input text.

	Returns:
		list[int]: Sorted newline positions.
	"""
	newlines: list[int] = []
	pos = text.find("\n")
	while pos != -1:
		newlines.append(pos)
		pos = text.find("\n", pos + 1)
	return newlines


#============================================


def pos_to_line(newlines: list[int], pos: int) -> int:
	"""
	Map a byte offset to 1-based line number using a newline index.

	Args:
		newlines: Sorted newline positions.
		pos: Character position in text.

	Returns:
		int: 1-based line number.
	"""
	return bisect.bisect_left(newlines, pos) + 1


#============================================


def _scan_heredoc_terminator(line: str) -> str | None:
	"""
	Detect a heredoc introducer outside of strings and return its terminator token.

	Args:
		line: Single line of text.

	Returns:
		str | None: Terminator token, if present.
	"""
	in_sq = False
	in_dq = False
	escape = False
	i = 0
	while i < len(line) - 1:
		ch = line[i]
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

		if (not in_sq) and (not in_dq) and (ch == "<") and (line[i + 1] == "<"):
			j = i + 2
			if j < len(line) and line[j] == "-":
				j += 1
			while j < len(line) and line[j].isspace():
				j += 1
			if j >= len(line):
				return None

			if line[j] in ("'", '"'):
				quote = line[j]
				j += 1
				start = j
				while j < len(line) and line[j] != quote:
					j += 1
				if j >= len(line):
					return None
				return line[start:j]

			start = j
			if not (line[j].isalpha() or line[j] == "_"):
				return None
			j += 1
			while j < len(line) and (line[j].isalnum() or line[j] == "_"):
				j += 1
			return line[start:j]

		i += 1

	return None


#============================================


def _strip_line_comment_preserving_strings(line: str) -> str:
	"""
	Strip a Perl-style comment from a line while preserving strings.

	Args:
		line: Single line of text.

	Returns:
		str: Line with trailing comment removed.
	"""
	in_sq = False
	in_dq = False
	escape = False
	for i, ch in enumerate(line):
		if escape:
			escape = False
			continue
		if ch == "\\":
			escape = True
			continue
		if (not in_dq) and (ch == "'") and (not in_sq):
			in_sq = True
			continue
		if in_sq and ch == "'":
			in_sq = False
			continue
		if (not in_sq) and (ch == '"') and (not in_dq):
			in_dq = True
			continue
		if in_dq and ch == '"':
			in_dq = False
			continue
		if (not in_sq) and (not in_dq) and ch == "#":
			trimmed = line[:i]
			if line.endswith("\n"):
				trimmed = trimmed + "\n"
			return trimmed
	return line


#============================================


def strip_comments(text: str) -> str:
	"""
	Remove Perl line comments, preserving strings and heredocs.

	Args:
		text: Full file contents.

	Returns:
		str: Text with comments removed.
	"""
	out_lines: list[str] = []
	heredoc_end: str | None = None

	for line in text.splitlines(keepends=True):
		if heredoc_end is not None:
			out_lines.append(line)
			if line.strip() == heredoc_end:
				heredoc_end = None
			continue

		heredoc_end = _scan_heredoc_terminator(line)
		clean_line = _strip_line_comment_preserving_strings(line)
		out_lines.append(clean_line)

	return "".join(out_lines)


#============================================


def strip_heredocs(text: str) -> str:
	"""
	Remove heredoc bodies while preserving line count.

	Args:
		text: Full file contents.

	Returns:
		str: Text with heredoc bodies removed.
	"""
	out_lines: list[str] = []
	heredoc_end: str | None = None

	for line in text.splitlines(keepends=True):
		if heredoc_end is None:
			heredoc_end = _scan_heredoc_terminator(line)
			out_lines.append(line)
			continue

		if line.strip() == heredoc_end:
			out_lines.append("\n" if line.endswith("\n") else "")
			heredoc_end = None
			continue

		out_lines.append("\n" if line.endswith("\n") else "")

	return "".join(out_lines)


#============================================


def _compile_name_rx(names: set[str]) -> re.Pattern:
	"""
	Compile a regex that matches any of the provided call names.

	Args:
		names: Set of function names to match.

	Returns:
		re.Pattern: Compiled regex.
	"""
	parts: list[str] = []
	for name in sorted(names):
		parts.append(re.escape(name))
	pat = r"(?:" + "|".join(parts) + r")"
	compiled = re.compile(r"(?<![A-Za-z0-9_])" + pat + r"(?![A-Za-z0-9_])")
	return compiled


#============================================


def iter_calls(text: str, names: set[str], newlines: list[int] | None = None) -> list[dict[str, object]]:
	"""
	Find function-like calls name(...) with balanced parentheses.

	Args:
		text: Input text (comments and heredocs already stripped).
		names: Function names to match.
		newlines: Optional newline index.

	Returns:
		list[dict[str, object]]: Call metadata dicts.
	"""
	calls: list[dict[str, object]] = []
	if not names:
		return calls

	if newlines is None:
		newlines = build_newline_index(text)

	name_rx = _compile_name_rx(names)
	i = 0
	while True:
		m = name_rx.search(text, i)
		if not m:
			break

		name = m.group(0)
		j = m.end()
		while j < len(text) and text[j].isspace():
			j += 1
		if j >= len(text) or text[j] != "(":
			i = m.end()
			continue

		start = j
		depth = 0
		in_sq = False
		in_dq = False
		escape = False
		k = j
		end = None
		while k < len(text):
			ch = text[k]
			if escape:
				escape = False
				k += 1
				continue
			if ch == "\\":
				escape = True
				k += 1
				continue
			if (not in_dq) and (ch == "'") and (not in_sq):
				in_sq = True
				k += 1
				continue
			if in_sq and ch == "'":
				in_sq = False
				k += 1
				continue
			if (not in_sq) and (ch == '"') and (not in_dq):
				in_dq = True
				k += 1
				continue
			if in_dq and ch == '"':
				in_dq = False
				k += 1
				continue

			if (not in_sq) and (not in_dq):
				if ch == "(":
					depth += 1
				elif ch == ")":
					depth -= 1
					if depth == 0:
						end = k + 1
						break
			k += 1

		if end is None:
			i = m.end()
			continue

		arg_text = text[start + 1 : end - 1]
		line = pos_to_line(newlines, m.start())
		call = {
			"name": name,
			"arg_text": arg_text,
			"start": start,
			"end": end,
			"line": line,
		}
		calls.append(call)
		i = end

	return calls


#============================================


def extract_loaded_macros(stripped_text: str) -> set[str]:
	"""
	Extract macro filenames from loadMacros calls.

	Args:
		stripped_text: Comment- and heredoc-stripped text.

	Returns:
		set[str]: Lowercased macro filenames.
	"""
	macros: set[str] = set()
	calls = iter_calls(stripped_text, MACRO_CALL_NAMES)
	for call in calls:
		if call["name"] != "loadMacros":
			continue
		arg_text = str(call["arg_text"])
		for match in FILENAME_RX.finditer(arg_text):
			filename = match.group(1)
			base = os.path.basename(filename).lower()
			macros.add(base)
	return macros


#============================================


def extract_assigned_vars(stripped_text: str) -> set[str]:
	"""
	Extract Perl variable names that appear declared or assigned.

	Recognizes:
	- Scalar declarations/assignments: my $var, $var =
	- Array/hash declarations/assignments: my @arr, @arr =, my %hash, %hash =
	- List assignments: ($a, $b, $c) = func()
	- Array element assignments: $arr[0] = (creates @arr via autovivification)
	- Hash element assignments: $hash{key} = (creates %hash via autovivification)

	Args:
		stripped_text: Comment- and heredoc-stripped text.

	Returns:
		set[str]: Variable names without leading sigil ($/@/%).
	"""
	vars_found: set[str] = set()

	# Scalar declarations: my $var, our $var
	for match in VAR_DECL_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	# Scalar assignments: $var =
	for match in VAR_ASSIGN_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	# Array/hash declarations: my @arr, my %hash
	for match in ARRAY_HASH_DECL_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	# Array/hash assignments: @arr =, %hash =
	for match in ARRAY_HASH_ASSIGN_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	# List assignments: ($a, $b, $c) = func()
	# Extract all variables from within the parentheses
	for match in LIST_ASSIGN_RX.finditer(stripped_text):
		# Get the full list assignment
		list_part = match.group(0)
		# Extract individual variables from the list
		for var_match in LIST_VAR_RX.finditer(list_part):
			vars_found.add(var_match.group(1))

	# Array element assignments: $arr[0] = value (autovivification)
	# This creates @arr, so we add 'arr' to the set
	for match in ARRAY_ELEM_ASSIGN_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	# Hash element assignments: $hash{key} = value (autovivification)
	# This creates %hash, so we add 'hash' to the set
	for match in HASH_ELEM_ASSIGN_RX.finditer(stripped_text):
		vars_found.add(match.group(1))

	return vars_found


#============================================


def detect_pgml_usage(stripped_text: str) -> bool:
	"""
	Detect PGML usage signals in stripped text.

	Args:
		stripped_text: Comment- and heredoc-stripped text.

	Returns:
		bool: True if PGML usage is detected.
	"""
	if re.search(r"(?m)^[ \t]*BEGIN_PGML", stripped_text):
		return True
	if re.search(r"\bPGML::Format\b", stripped_text):
		return True
	if re.search(r"\bPGML::", stripped_text):
		return True
	return False


#============================================


def extract_block_markers(text: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
	"""
	Check BEGIN/END markers with a stack and collect PGML regions.

	Args:
		text: Full file contents.

	Returns:
		tuple[list[dict[str, object]], list[dict[str, object]]]: Issues and PGML regions.
	"""
	issues: list[dict[str, object]] = []
	pgml_regions: list[dict[str, object]] = []
	stack: list[dict[str, object]] = []

	heredoc_end: str | None = None
	pos = 0
	line_num = 0
	for line in text.splitlines(keepends=True):
		line_num += 1
		if heredoc_end is not None:
			if line.strip() == heredoc_end:
				heredoc_end = None
			pos += len(line)
			continue

		heredoc_end = _scan_heredoc_terminator(line)
		if heredoc_end is not None:
			pos += len(line)
			continue

		match = BLOCK_MARKER_RX.search(line)
		if not match:
			pos += len(line)
			continue

		action = match.group(1)
		tag = match.group(2)
		full_tag = f"{action}_{tag}"

		if action == "BEGIN":
			if tag in {"PGML_HINT", "PGML_SOLUTION"}:
				if any(item["tag"].startswith("PGML") for item in stack):
					message = f"{full_tag} appears inside another PGML block"
					issue = {"severity": "WARNING", "message": message, "line": line_num}
					issues.append(issue)
			start_pos = pos + len(line)
			entry = {"tag": tag, "start": start_pos, "line": line_num}
			stack.append(entry)
			pos += len(line)
			continue

		if action == "END":
			if not stack:
				message = f"{full_tag} without matching BEGIN"
				issue = {"severity": "ERROR", "message": message, "line": line_num}
				issues.append(issue)
				pos += len(line)
				continue

			open_entry = stack[-1]
			if open_entry["tag"] != tag:
				message = f"{full_tag} does not match BEGIN_{open_entry['tag']}"
				issue = {"severity": "ERROR", "message": message, "line": line_num}
				issues.append(issue)
				pos += len(line)
				continue

			stack.pop()
			if tag.startswith("PGML"):
				region = {
					"start": open_entry["start"],
					"end": pos,
					"kind": f"BEGIN_{tag}",
					"line": open_entry["line"],
				}
				pgml_regions.append(region)
			pos += len(line)
			continue

		pos += len(line)

	for open_entry in stack:
		message = f"BEGIN_{open_entry['tag']} without matching END"
		line = int(open_entry["line"])
		issue = {"severity": "ERROR", "message": message, "line": line}
		issues.append(issue)

	return issues, pgml_regions


#============================================


def extract_pgml_heredoc_regions(text: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
	"""
	Extract PGML heredoc regions and report unterminated blocks.

	Args:
		text: Full file contents.

	Returns:
		tuple[list[dict[str, object]], list[dict[str, object]]]: Issues and regions.
	"""
	issues: list[dict[str, object]] = []
	regions: list[dict[str, object]] = []

	heredoc_end: str | None = None
	body_start: int | None = None
	body_line: int | None = None
	is_pgml = False

	pos = 0
	line_num = 0
	for line in text.splitlines(keepends=True):
		line_num += 1
		if heredoc_end is None:
			terminator = _scan_heredoc_terminator(line)
			if terminator is None:
				pos += len(line)
				continue
			is_pgml = "PGML" in terminator or (re.search(r"\bPGML::", line) is not None)
			heredoc_end = terminator
			body_start = pos + len(line)
			body_line = line_num + 1
			pos += len(line)
			continue

		if line.strip() == heredoc_end:
			if is_pgml and body_start is not None:
				region = {
					"start": body_start,
					"end": pos,
					"kind": "HEREDOC_PGML",
					"line": body_line,
				}
				regions.append(region)
			heredoc_end = None
			body_start = None
			body_line = None
			is_pgml = False
			pos += len(line)
			continue

		pos += len(line)

	if heredoc_end is not None and is_pgml:
		line = 1
		if body_line is not None:
			line = body_line - 1
		message = f"PGML heredoc terminator '{heredoc_end}' not found"
		issue = {"severity": "ERROR", "message": message, "line": line}
		issues.append(issue)

	return issues, regions
