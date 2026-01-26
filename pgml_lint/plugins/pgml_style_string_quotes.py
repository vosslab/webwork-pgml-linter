# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_style_string_quotes"
PLUGIN_NAME = "PGML style strings with unescaped quotes"
DEFAULT_ENABLED = True

UNESCAPED_SINGLE_QUOTE_RX = re.compile(r"(?<!\\)'")


#============================================


def _extract_style_payloads(text: str, start: int) -> tuple[list[str], int] | None:
	"""
	Extract PGML style payloads starting at a [<...>] marker.

	Args:
		text: Full file contents.
		start: Index where "[<" begins.

	Returns:
		tuple[list[str], int] | None: Payload list and end index, or None.
	"""
	if text[start:start + 2] != "[<":
		return None

	line_end = text.find("\n", start)
	if line_end == -1:
		line_end = len(text)

	label_end = text.find(">]", start + 2, line_end)
	if label_end == -1:
		return None

	cursor = label_end + 2
	payloads: list[str] = []
	while cursor + 1 < line_end and text[cursor:cursor + 2] == "{[":
		close = text.find("]}", cursor + 2, line_end)
		if close == -1:
			return None
		payloads.append(text[cursor + 2:close])
		cursor = close + 2

	if not payloads:
		return None

	return payloads, cursor


#============================================


def _collect_pgml_regions(context: dict[str, object]) -> list[tuple[int, int]]:
	"""
	Collect PGML regions to ignore during scanning.

	Args:
		context: Shared lint context.

	Returns:
		list[tuple[int, int]]: List of (start, end) regions.
	"""
	regions: list[tuple[int, int]] = []
	pgml_regions_obj = context.get("pgml_regions", [])
	if not isinstance(pgml_regions_obj, list):
		return regions

	for region in pgml_regions_obj:
		if not isinstance(region, dict):
			continue
		start = region.get("start")
		end = region.get("end")
		if not isinstance(start, int) or not isinstance(end, int):
			continue
		if start >= end:
			continue
		regions.append((start, end))

	regions.sort()
	return regions


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when PGML style strings in single quotes use unescaped quotes.

	Perl single-quoted strings cannot contain raw single quotes. PGML style
	markup like [<label>]{['span', style => 'color: #...;']} must either
	escape single quotes (\\') or use double quotes/q{...}.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []
	regions = _collect_pgml_regions(context)

	region_idx = 0
	in_sq = False
	in_dq = False
	escape = False
	i = 0
	while i < len(text):
		if region_idx < len(regions) and i >= regions[region_idx][1]:
			region_idx += 1
			continue
		if region_idx < len(regions) and regions[region_idx][0] <= i < regions[region_idx][1]:
			i = regions[region_idx][1]
			in_sq = False
			in_dq = False
			escape = False
			continue

		ch = text[i]

		if not in_sq and not in_dq and ch == "#":
			line_end = text.find("\n", i)
			if line_end == -1:
				break
			i = line_end + 1
			continue

		if in_sq and text[i:i + 2] == "[<":
			result = _extract_style_payloads(text, i)
			if result is not None:
				payloads, _ = result
				if any(UNESCAPED_SINGLE_QUOTE_RX.search(payload) for payload in payloads):
					line = pgml_lint.parser.pos_to_line(newlines, i)
					message = (
						"PGML style tag inside single-quoted string contains unescaped single quotes; "
						"escape as \\' or use double quotes or q{...}"
					)
					issue = {"severity": "ERROR", "message": message, "line": line}
					issues.append(issue)

		if in_sq or in_dq:
			if escape:
				escape = False
				i += 1
				continue
			if ch == "\\":
				escape = True
				i += 1
				continue
			if in_sq and ch == "'":
				in_sq = False
				i += 1
				continue
			if in_dq and ch == '"':
				in_dq = False
				i += 1
				continue
		else:
			if ch == "'":
				in_sq = True
				i += 1
				continue
			if ch == '"':
				in_dq = True
				i += 1
				continue

		i += 1

	return issues
