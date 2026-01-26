# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_pgml_wrapper_in_string"
PLUGIN_NAME = "PGML tag wrapper in Perl strings"
DEFAULT_ENABLED = True

STRING_RX = re.compile(r"('([^'\\\\]|\\\\.)*'|\"([^\"\\\\]|\\\\.)*\")")
PGML_WRAPPER_TOKENS = ("[<", "]{[", ">]{", "}{[")


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when PGML tag wrapper syntax appears inside Perl string literals.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))

	for line_num, line in enumerate(text.splitlines(), start=1):
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		for match in STRING_RX.finditer(clean):
			literal = match.group(0)
			for token in PGML_WRAPPER_TOKENS:
				if token in literal:
					message = (
						"PGML tag wrapper syntax found inside a Perl string; "
						"PGML parses once and will not re-parse strings"
					)
					issue = {"severity": "WARNING", "message": message, "line": line_num}
					issues.append(issue)
					break
	return issues
