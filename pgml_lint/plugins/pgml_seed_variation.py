# Standard Library
import re

# Local modules
import pgml_lint.parser

PLUGIN_ID = "pgml_seed_variation"
PLUGIN_NAME = "Seed variation detection"
DEFAULT_ENABLED = True

RANDOMIZATION_PATTERNS = [
	r"\brandom\s*\(",
	r"\bnon_zero_random\s*\(",
	r"\blist_random\s*\(",
	r"\brandom_subset\s*\(",
	r"\brandom_coprime\s*\(",
	r"\brandom_pairwise_coprime\s*\(",
	r"\bNchooseK\s*\(",
	r"\bshuffle\s*\(",
	r"\bshufflemap\s*\(",
	r"\brandomPermutation\s*\(",
	r"\brandomPrime\s*\(",
	r"\brandom_inv_matrix\s*\(",
	r"\brandom_diag_matrix\s*\(",
	r"\burand\s*\(",
	r"\bexprand\s*\(",
	r"\bpoissonrand\s*\(",
	r"\bbinomrand\s*\(",
	r"\bbernoullirand\s*\(",
	r"\bdiscreterand\s*\(",
	r"\bGRgraph_size_random\s*\(",
	r"\bGRgraph_size_random_weight_dweight\s*\(",
	r"\bGRgraphpic_dim_random_labels_weight_dweight\s*\(",
	r"\brandomPerson\s*\(",
	r"\brandomLastName\s*\(",
	r"\blist_random_multi_uniq\s*\(",
	r"\bbkell_list_random_selection\s*\(",
	r"\bProblemRandomize\s*\(",
	r"\bPeriodicRerandomization\s*\(",
	r"\brand_button\s*\(",
	r"\brandomizeCheckbox\s*\(",
	r"\brandomizeButton\s*\(",
	r"\brandomizeInput\s*\(",
	r"\brandomizeHTML\s*\(",
	r"\bSRAND\s*\(",
	r"\bPGrandom\b",
	r"\bPG_random_generator\b",
	r"\brand\s*\(",
	r"\$problemSeed\b",
	r"\$PG_original_problemSeed\b",
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
	Warn when no seed-based variation is detected.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	should_check = bool(re.search(r"\bDOCUMENT\s*\(\s*\)", text))
	if not should_check:
		return issues

	lines = text.splitlines()
	for line in lines:
		clean = pgml_lint.parser._strip_line_comment_preserving_strings(line)
		mask = _mask_strings(clean)
		for pattern_text in RANDOMIZATION_PATTERNS:
			pattern = re.compile(pattern_text)
			for match in pattern.finditer(clean):
				if mask[match.start()]:
					continue
				return issues

	message = "No seed-based randomization detected; answer may not vary with seed"
	issue = {"severity": "WARNING", "message": message}
	issues.append(issue)
	return issues
