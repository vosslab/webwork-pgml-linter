# Standard Library
import re

PLUGIN_ID = "pgml_ans_style"
PLUGIN_NAME = "PGML answer style consistency"
DEFAULT_ENABLED = True

# Match ANS(...) calls outside of comments
# Looks for ANS( followed by anything until balanced closing paren
ANS_CALL_RX = re.compile(
	r"(?m)^[ \t]*ANS\s*\(",
)


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when ANS() calls appear after END_PGML blocks (mixing styles).

	Pure PGML style uses inline answer specs like [_]{$answer}.
	Old PG style uses ANS($answer->cmp()) after the text block.
	Mixing these styles is inconsistent.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	source = str(context.get("text", ""))
	newlines_obj = context.get("newlines")
	if not isinstance(newlines_obj, list):
		return issues
	newlines: list[int] = newlines_obj

	if not source or not newlines:
		return issues

	# Find all END_PGML blocks
	end_pgml_pattern = re.compile(r"(?m)^[ \t]*END_PGML\b")
	end_pgml_matches = list(end_pgml_pattern.finditer(source))

	if not end_pgml_matches:
		return issues

	# For each END_PGML, check if there are ANS() calls after it
	for match in end_pgml_matches:
		end_pgml_pos = match.end()

		# Find the next ENDDOCUMENT or end of file
		enddoc_pattern = re.compile(r"(?m)^[ \t]*ENDDOCUMENT\s*\(")
		enddoc_match = enddoc_pattern.search(source, end_pgml_pos)
		search_end = enddoc_match.start() if enddoc_match else len(source)

		# Search for ANS() calls in this region
		region = source[end_pgml_pos:search_end]
		ans_matches = list(ANS_CALL_RX.finditer(region))

		for ans_match in ans_matches:
			# Calculate the absolute position in the source
			ans_pos = end_pgml_pos + ans_match.start()

			# Calculate line number
			line_num = 1
			for newline_pos in newlines:
				if newline_pos < ans_pos:
					line_num += 1
				else:
					break

			message = (
				"ANS() call after END_PGML block (mixed style). "
				"Pure PGML uses inline answer specs: [_]{$answer} instead of ANS($answer->cmp())"
			)
			issue = {
				"severity": "WARNING",
				"line": line_num,
				"message": message,
			}
			issues.append(issue)

	return issues
