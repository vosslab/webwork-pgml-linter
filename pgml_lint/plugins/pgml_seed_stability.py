# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_seed_stability"
PLUGIN_NAME = "Seed stability checks"
DEFAULT_ENABLED = True

UNSEEDED_PATTERNS = [
	(r"\brand\s*\(", "rand() may bypass PG seeding; use random() or list_random()."),
	(r"\bsrand\s*\(", "srand() overrides PG seeding; avoid for stable seeds."),
	(r"\btime\s*\(", "time() makes values depend on the clock; avoid for stable seeds."),
	(r"\blocaltime\s*\(", "localtime() makes values depend on the clock; avoid for stable seeds."),
	(r"\bgmtime\s*\(", "gmtime() makes values depend on the clock; avoid for stable seeds."),
	(r"\bSRAND\s*\(", "SRAND() resets the PG random generator; avoid for stable seeds."),
	(r"\bProblemRandomize\s*\(", "ProblemRandomize() reseeds across attempts; confirm this is intended."),
	(r"\bPeriodicRerandomization\s*\(", "PeriodicRerandomization() reseeds by attempt; confirm this is intended."),
	(r"\brand_button\s*\(", "rand_button() can reseed problems; confirm this is intended."),
	(r"\brandomizeCheckbox\s*\(", "randomizeCheckbox() can reseed problems; confirm this is intended."),
	(r"\brandomizeButton\s*\(", "randomizeButton() can reseed problems; confirm this is intended."),
	(r"\brandomizeInput\s*\(", "randomizeInput() can reseed problems; confirm this is intended."),
	(r"\brandomizeHTML\s*\(", "randomizeHTML() can reseed problems; confirm this is intended."),
]


#============================================


def _mask_strings(line: str) -> list[bool]:
	"""
	Return a mask for positions inside strings.
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
	Warn when non-seeded randomness or clock calls appear in PG code.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))

	lines = text.splitlines()
	for line_num, line in enumerate(lines, start=1):
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		mask = _mask_strings(clean)
		for pattern_text, message in UNSEEDED_PATTERNS:
			pattern = re.compile(pattern_text)
			for match in pattern.finditer(clean):
				if mask[match.start()]:
					continue
				before = clean[: match.start()]
				if re.search(r"(->|::)\s*$", before):
					continue
				issue = {
					"severity": "WARNING",
					"message": message,
					"line": line_num,
				}
				issues.append(issue)
	return issues
