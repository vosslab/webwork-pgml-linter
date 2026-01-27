# Standard Library
import re

# Local modules
import pgml_lint.parser
import pgml_lint.pgml
import pgml_lint.pg_version

PLUGIN_ID = "pgml_modes_in_inline"
PLUGIN_NAME = "MODES inside inline eval blocks"
DEFAULT_ENABLED = True

MODES_RX = re.compile(r"\bMODES\s*\(")
TEX_EMPTY_RX = re.compile(r"\bTeX\s*=>\s*(['\"])\s*\1")
HTML_STRING_RX = re.compile(r"\bHTML\s*=>\s*(['\"])(.*?)\1", re.DOTALL)
ALLOWED_HTML_TAGS = (
	"<div",
	"</div",
	"<span",
	"</span",
	"<br",
	"<sup",
	"</sup",
	"<sub",
	"</sub",
)


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


def _iter_modes_args(text: str) -> list[str]:
	"""
	Extract MODES() argument payloads from text.
	"""
	payloads: list[str] = []
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
		payloads.append(payload)
		cursor = end_pos
	return payloads


#============================================


def _html_only_layout_ok(payload: str) -> bool:
	"""
	Return True when MODES payload uses HTML-only layout with empty TeX.
	"""
	if TEX_EMPTY_RX.search(payload) is None:
		return False
	html_match = HTML_STRING_RX.search(payload)
	if html_match is None:
		return False
	html_value = html_match.group(2).lower()
	return any(tag in html_value for tag in ALLOWED_HTML_TAGS)


#============================================


def _html_only_layout_needs_tex_empty(payload: str) -> bool:
	"""
	Return True when HTML layout tags appear but TeX is not empty.
	"""
	html_match = HTML_STRING_RX.search(payload)
	if html_match is None:
		return False
	html_value = html_match.group(2).lower()
	if not any(tag in html_value for tag in ALLOWED_HTML_TAGS):
		return False
	return TEX_EMPTY_RX.search(payload) is None


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when MODES() appears inside [@ @] inline blocks.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("text", ""))
	newlines_obj = context.get("newlines", [])
	newlines = list(newlines_obj) if isinstance(newlines_obj, list) else []
	regions = context.get("pgml_regions", [])

	pg_version_raw = pgml_lint.pg_version.normalize_pg_version(
		context.get("pg_version")
	)
	pg_version_tuple: tuple[int, int] | None
	try:
		pg_version_tuple = pgml_lint.pg_version.parse_pg_version(pg_version_raw)
	except ValueError:
		pg_version_tuple = None
	pg_217_compat = (
		pg_version_tuple is not None and pg_version_tuple <= (2, 17)
	)

	inline_spans_by_region: list[list[tuple[int, int]]] = []
	inline_spans_obj = context.get("pgml_inline_spans", [])
	if isinstance(inline_spans_obj, list):
		inline_spans_by_region = inline_spans_obj

	for region_idx, region in enumerate(regions):
		start = int(region.get("start", 0))
		end = int(region.get("end", 0))
		block_text = text[start:end]

		inline_spans: list[tuple[int, int]] = []
		if region_idx < len(inline_spans_by_region):
			inline_spans = inline_spans_by_region[region_idx]
		else:
			inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
				block_text,
				start,
				newlines,
			)
			issues.extend(inline_issues)

		for span_start, span_end in inline_spans:
			inline_text = block_text[span_start + 2 : span_end - 2]
			if MODES_RX.search(inline_text) is None:
				continue

			payloads = _iter_modes_args(inline_text)
			if not payloads:
				payloads = [inline_text]

			message = ""
			if pg_217_compat:
				for payload in payloads:
					if _html_only_layout_ok(payload):
						continue
					if _html_only_layout_needs_tex_empty(payload):
						message = (
							"MODES() inside [@ @] uses raw HTML layout; "
							"use TeX => '' for PG 2.17"
						)
						break
					message = (
						"MODES() used inside [@ @] block; MODES returns 1 in eval context and "
						"will not emit HTML"
					)
					break
				if not message:
					continue
			else:
				message = (
					"MODES() used inside [@ @] block; MODES returns 1 in eval context and "
					"will not emit HTML"
				)

			line = pgml_lint.parser.pos_to_line(newlines, start + span_start)
			issue = {"severity": "WARNING", "message": message, "line": line}
			issues.append(issue)

	return issues
