# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_include_pgproblem"
PLUGIN_NAME = "includePGproblem usage"
DEFAULT_ENABLED = True

INCLUDE_RX = re.compile(r"\bincludePGproblem\s*\(")


#============================================


def _strip_loadmacros(lines: list[str]) -> list[str]:
	"""
	Remove loadMacros(...) blocks from lines.
	"""
	out_lines: list[str] = []
	in_load = False
	for line in lines:
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		if not in_load and "loadMacros" in clean:
			in_load = True
			if ");" in clean:
				in_load = False
			continue
		if in_load:
			if ");" in clean:
				in_load = False
			continue
		out_lines.append(clean)
	return out_lines


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on includePGproblem usage and include-only stubs.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))

	line_num = 0
	include_lines: list[int] = []
	lines = text.splitlines()
	for line in lines:
		line_num += 1
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		if INCLUDE_RX.search(clean):
			include_lines.append(line_num)

	if not include_lines:
		return issues

	for line in include_lines:
		message = "includePGproblem() used; target file not verified by linter"
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	filtered_lines = _strip_loadmacros(lines)
	payload_lines: list[str] = []
	for line in filtered_lines:
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line).strip()
		if clean == "":
			continue
		if INCLUDE_RX.search(clean):
			continue
		if re.match(r"^\s*DOCUMENT\s*\(\s*\)\s*;?\s*$", clean):
			continue
		if re.match(r"^\s*ENDDOCUMENT\s*\(\s*\)\s*;?\s*$", clean):
			continue
		payload_lines.append(clean)

	if not payload_lines:
		message = "includePGproblem() appears to be the only content in this file"
		issue = {"severity": "WARNING", "message": message, "line": include_lines[0]}
		issues.append(issue)

	return issues
