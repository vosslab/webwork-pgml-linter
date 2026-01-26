# Standard Library
import re

PLUGIN_ID = "pgml_header_tags"
PLUGIN_NAME = "PG header tag quality"
DEFAULT_ENABLED = True

NOISY_DBSUBJECTS = {
	"",
	"WeBWorK",
	"ZZZ-Inserted Text",
	"Subject",
	"TBA",
	"History",
	"NECAP",
	"Middle School",
	"Elementary School",
	"Demos",
	"algeba",
}

PLACEHOLDER_RX = re.compile(r"refer to|taxonomy", re.IGNORECASE)
KEYWORDS_RX = re.compile(r"^##\s*KEYWORDS\s*\((.*)\)\s*$")
SMART_QUOTES_RX = re.compile(r"[\u2018\u2019\u201c\u201d\u2013\u2014]")


#============================================


def _extract_header_lines(text: str) -> list[tuple[int, str]]:
	"""
	Extract leading header comment lines.
	"""
	lines: list[tuple[int, str]] = []
	in_header = True
	line_num = 0
	for line in text.splitlines():
		line_num += 1
		if line.strip() == "":
			if in_header:
				continue
			break
		if line.lstrip().startswith("##"):
			lines.append((line_num, line))
			continue
		in_header = False
		break
	return lines


#============================================


def _parse_tag_value(line: str, tag: str) -> str | None:
	"""
	Parse a header tag value from a single line.
	"""
	prefix = f"## {tag}"
	if not line.lstrip().startswith(prefix):
		return None
	start = line.find("(")
	end = line.rfind(")")
	if start == -1 or end == -1 or end <= start:
		return ""
	value = line[start + 1:end].strip()
	if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
		value = value[1:-1].strip()
	return value


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on noisy or placeholder header tags.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	header_lines = _extract_header_lines(text)

	dbsubject: str | None = None
	dbchapter: str | None = None
	dbsection: str | None = None
	dbsubject_line: int | None = None
	dbchapter_line: int | None = None
	dbsection_line: int | None = None
	keywords_raw: str | None = None
	keywords_line: int | None = None
	description_start_line: int | None = None
	description_end_line: int | None = None
	description_content: list[str] = []
	in_description = False

	for line_num, line in header_lines:
		if SMART_QUOTES_RX.search(line):
			message = "Header contains smart quotes or non-ASCII punctuation"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)

		if line.lstrip().startswith("## DESCRIPTION"):
			description_start_line = line_num
			in_description = True
			continue
		if line.lstrip().startswith("## ENDDESCRIPTION"):
			description_end_line = line_num
			in_description = False
			continue
		if in_description:
			content = line.lstrip()[2:].strip()
			if content != "":
				description_content.append(content)

		if line.lstrip().startswith("## KEYWORDS"):
			match = KEYWORDS_RX.match(line.strip())
			if match is None:
				message = "KEYWORDS tag is malformed; expected KEYWORDS('k1','k2',...)"
				issue = {"severity": "WARNING", "message": message, "line": line_num}
				issues.append(issue)
			elif keywords_raw is None:
				keywords_raw = match.group(1).strip()
				keywords_line = line_num

		value = _parse_tag_value(line, "DBsubject")
		if value is not None:
			dbsubject = value
			dbsubject_line = line_num
			continue
		value = _parse_tag_value(line, "DBchapter")
		if value is not None:
			dbchapter = value
			dbchapter_line = line_num
			continue
		value = _parse_tag_value(line, "DBsection")
		if value is not None:
			dbsection = value
			dbsection_line = line_num
			continue

	if description_start_line is None and description_end_line is not None:
		message = "ENDDESCRIPTION present without DESCRIPTION"
		issue = {"severity": "WARNING", "message": message, "line": description_end_line}
		issues.append(issue)
	if description_start_line is None:
		message = "Missing DESCRIPTION block in header"
		issue = {"severity": "WARNING", "message": message, "line": 1}
		issues.append(issue)
	elif description_end_line is None:
		message = "DESCRIPTION block missing ENDDESCRIPTION"
		issue = {"severity": "WARNING", "message": message, "line": description_start_line}
		issues.append(issue)
	else:
		if len(description_content) == 0:
			message = "DESCRIPTION block is empty"
			issue = {"severity": "WARNING", "message": message, "line": description_start_line}
			issues.append(issue)
		if len(description_content) > 4:
			message = "DESCRIPTION block is long; keep to 1-4 sentences"
			issue = {"severity": "WARNING", "message": message, "line": description_start_line}
			issues.append(issue)

	if keywords_raw is None:
		message = "Missing KEYWORDS tag in header"
		issue = {"severity": "WARNING", "message": message, "line": 1}
		issues.append(issue)
	else:
		keywords: list[str] = []
		for match in re.finditer(r"['\"]([^'\"]*)['\"]", keywords_raw):
			value = match.group(1).strip()
			if value != "":
				keywords.append(value)
		if len(keywords) == 0:
			for chunk in keywords_raw.split(","):
				value = chunk.strip().strip("'\"")
				if value != "":
					keywords.append(value)

		if len(keywords) == 0:
			message = "KEYWORDS tag is empty"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": keywords_line or 1,
			}
			issues.append(issue)
		else:
			if len(keywords) < 3:
				message = "KEYWORDS should include at least 3 entries"
				issue = {
					"severity": "WARNING",
					"message": message,
					"line": keywords_line or 1,
				}
				issues.append(issue)
			if len(keywords) > 10:
				message = "KEYWORDS should include at most 10 entries"
				issue = {
					"severity": "WARNING",
					"message": message,
					"line": keywords_line or 1,
				}
				issues.append(issue)

			seen: set[str] = set()
			dupes: set[str] = set()
			for keyword in keywords:
				key = keyword.lower()
				if key in seen:
					dupes.add(keyword)
				seen.add(key)
			if dupes:
				joined = ", ".join(sorted(dupes))
				message = f"KEYWORDS contains duplicates: {joined}"
				issue = {
					"severity": "WARNING",
					"message": message,
					"line": keywords_line or 1,
				}
				issues.append(issue)

	if dbsubject is None:
		message = "Missing DBsubject tag in header"
		issue = {"severity": "WARNING", "message": message, "line": 1}
		issues.append(issue)
	else:
		normalized = dbsubject.strip()
		if normalized in NOISY_DBSUBJECTS:
			message = f"DBsubject '{normalized}' is a placeholder or noisy value"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": dbsubject_line or 1,
			}
			issues.append(issue)

	if dbchapter is None:
		message = "Missing DBchapter tag in header"
		issue = {"severity": "WARNING", "message": message, "line": 1}
		issues.append(issue)
	else:
		normalized = dbchapter.strip()
		if normalized == "":
			message = "DBchapter is empty"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": dbchapter_line or 1,
			}
			issues.append(issue)
		if PLACEHOLDER_RX.search(normalized):
			message = "DBchapter uses placeholder reference text"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": dbchapter_line or 1,
			}
			issues.append(issue)

	if dbsection is None:
		message = "Missing DBsection tag in header"
		issue = {"severity": "WARNING", "message": message, "line": 1}
		issues.append(issue)
	else:
		normalized = dbsection.strip()
		if normalized == "":
			message = "DBsection is empty"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": dbsection_line or 1,
			}
			issues.append(issue)
		if PLACEHOLDER_RX.search(normalized):
			message = "DBsection uses placeholder reference text"
			issue = {
				"severity": "WARNING",
				"message": message,
				"line": dbsection_line or 1,
			}
			issues.append(issue)

	return issues
