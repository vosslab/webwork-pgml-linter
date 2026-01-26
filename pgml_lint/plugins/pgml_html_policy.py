# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_html_policy"
PLUGIN_NAME = "HTML policy checks"
DEFAULT_ENABLED = True

TAG_RULES = {
	"script": "ERROR",
	"iframe": "ERROR",
	"object": "ERROR",
	"embed": "ERROR",
	"style": "WARNING",
	"table": "ERROR",
	"tr": "ERROR",
	"td": "ERROR",
	"th": "ERROR",
	"thead": "ERROR",
	"tbody": "ERROR",
	"tfoot": "ERROR",
	"colgroup": "ERROR",
	"col": "ERROR",
	"form": "WARNING",
	"input": "WARNING",
	"textarea": "WARNING",
	"button": "WARNING",
	"img": "WARNING",
	"a": "WARNING",
	"svg": "WARNING",
	"math": "WARNING",
	"canvas": "WARNING",
	"video": "WARNING",
	"audio": "WARNING",
}

TAG_RX = re.compile(r"<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)\b")
ESCAPED_TAG_RX = re.compile(r"&lt;\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)\b")
TEX2JAX_RX = re.compile(r"class\s*=\s*['\"][^'\"]*\btex2jax_ignore\b[^'\"]*['\"]")
PGML_WRAPPER_TAG_RX = re.compile(
	r"\[\s*<[^>]*>\s*\]\s*\{\s*\[\s*['\"]([a-zA-Z0-9]+)['\"]",
	re.IGNORECASE,
)


#============================================


def _in_region(pos: int, regions: list[dict[str, object]]) -> bool:
	"""
	Check if a position is inside any PGML block region.
	"""
	for region in regions:
		start = region.get("start")
		end = region.get("end")
		if not isinstance(start, int) or not isinstance(end, int):
			continue
		if start <= pos < end:
			return True
	return False


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


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on disallowed HTML tags outside PGML-safe paths.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []
	pgml_block_regions_obj = context.get("pgml_block_regions", [])
	pgml_block_regions = (
		list(pgml_block_regions_obj)
		if isinstance(pgml_block_regions_obj, list)
		else []
	)

	for line_num, line in enumerate(text.splitlines(), start=1):
		if "<style" in line.lower() and "header_text" not in line.lower():
			message = "Inline <style> tag found outside HEADER_TEXT; may be sanitized"
			issue = {"severity": "WARNING", "message": message, "line": line_num}
			issues.append(issue)

	for match in TEX2JAX_RX.finditer(text):
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = (
			"HTML class \"tex2jax_ignore\" found; MathJax is suppressed and output may not render"
		)
		issue = {"severity": "WARNING", "message": message, "line": line}
		issues.append(issue)

	for line_num, line in enumerate(text.splitlines(), start=1):
		mask = _mask_strings(line)
		for match in PGML_WRAPPER_TAG_RX.finditer(line):
			if match.start() < len(mask) and mask[match.start()]:
				continue
			tag = match.group(1).lower()
			if tag not in TAG_RULES:
				continue
			message = (
				f"PGML tag wrapper uses <{tag}> which is disallowed or sanitized in this install"
			)
			issue = {"severity": TAG_RULES[tag], "message": message, "line": line_num}
			issues.append(issue)

	for match in TAG_RX.finditer(text):
		tag = match.group(1).lower()
		if tag not in TAG_RULES:
			continue
		if tag in {"table", "tr", "td", "th", "thead", "tbody", "tfoot", "colgroup", "col"}:
			if _in_region(match.start(), pgml_block_regions):
				continue
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = f"HTML <{tag}> tag detected; avoid raw HTML that can be sanitized"
		issue = {"severity": TAG_RULES[tag], "message": message, "line": line}
		issues.append(issue)

	for match in ESCAPED_TAG_RX.finditer(text):
		tag = match.group(1).lower()
		if tag not in TAG_RULES:
			continue
		line = pgml_lint.parser.pos_to_line(newlines, match.start())
		message = f"Escaped HTML tag &lt;{tag}&gt; detected; output may be escaping HTML"
		issue = {"severity": "ERROR", "message": message, "line": line}
		issues.append(issue)

	return issues
