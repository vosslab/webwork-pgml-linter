# Standard Library
import re

PLUGIN_ID = "pgml_function_signatures"
PLUGIN_NAME = "Function signatures and empty args"
DEFAULT_ENABLED = True

TYPO_MAP = {
	"Popup": "PopUp",
	"Dropdown": "DropDown",
	"Radiobuttons": "RadioButtons",
	"Checkboxes": "CheckboxList",
}

FUNCTION_RULES = {
	"random": {"min": 3, "max": 3, "severity": "ERROR"},
	"NchooseK": {"min": 2, "max": 2, "severity": "ERROR"},
	"includePGproblem": {"min": 1, "max": None, "severity": "ERROR"},
	"Compute": {"min": 1, "max": None, "severity": "WARNING"},
	"Formula": {"min": 1, "max": None, "severity": "WARNING"},
	"Real": {"min": 1, "max": None, "severity": "WARNING"},
	"Vector": {"min": 1, "max": None, "severity": "WARNING"},
	"Matrix": {"min": 1, "max": None, "severity": "WARNING"},
	"DropDown": {"min": 2, "max": None, "severity": "WARNING"},
	"PopUp": {"min": 2, "max": None, "severity": "WARNING"},
	"RadioButtons": {"min": 1, "max": None, "severity": "WARNING"},
	"CheckboxList": {"min": 1, "max": None, "severity": "WARNING"},
	"NumberWithUnits": {"min": 1, "max": None, "severity": "WARNING"},
	"MultiAnswer": {"min": 1, "max": None, "severity": "WARNING"},
	"OneOf": {"min": 1, "max": None, "severity": "WARNING"},
	"FormulaUpToConstant": {"min": 1, "max": None, "severity": "WARNING"},
}

CALL_RX = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


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


def _parse_args(line: str, open_idx: int) -> tuple[list[str] | None, int]:
	"""
	Parse arguments for a single-line function call.
	"""
	args: list[str] = []
	current = []
	in_sq = False
	in_dq = False
	escape = False
	depth_paren = 0
	depth_bracket = 0
	depth_brace = 0

	i = open_idx + 1
	while i < len(line):
		ch = line[i]
		if escape:
			current.append(ch)
			escape = False
			i += 1
			continue
		if ch == "\\":
			current.append(ch)
			escape = True
			i += 1
			continue
		if in_sq:
			current.append(ch)
			if ch == "'":
				in_sq = False
			i += 1
			continue
		if in_dq:
			current.append(ch)
			if ch == '"':
				in_dq = False
			i += 1
			continue
		if ch == "'":
			current.append(ch)
			in_sq = True
			i += 1
			continue
		if ch == '"':
			current.append(ch)
			in_dq = True
			i += 1
			continue
		if ch == "(":
			depth_paren += 1
			current.append(ch)
			i += 1
			continue
		if ch == ")":
			if depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
				arg_text = "".join(current).strip()
				if args or arg_text != "":
					args.append(arg_text)
				return args, i
			depth_paren -= 1
			current.append(ch)
			i += 1
			continue
		if ch == "[":
			depth_bracket += 1
			current.append(ch)
			i += 1
			continue
		if ch == "]":
			depth_bracket = max(0, depth_bracket - 1)
			current.append(ch)
			i += 1
			continue
		if ch == "{":
			depth_brace += 1
			current.append(ch)
			i += 1
			continue
		if ch == "}":
			depth_brace = max(0, depth_brace - 1)
			current.append(ch)
			i += 1
			continue
		if ch == "," and depth_paren == 0 and depth_bracket == 0 and depth_brace == 0:
			args.append("".join(current).strip())
			current = []
			i += 1
			continue
		current.append(ch)
		i += 1
	return None, -1


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn on function signature mismatches and empty argument lists.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))

	lines = text.splitlines()
	for line_num, line in enumerate(lines, start=1):
		clean = line
		mask = _mask_strings(clean)
		for match in CALL_RX.finditer(clean):
			if mask[match.start()]:
				continue
			name = match.group(1)
			before = clean[: match.start()]
			if re.search(r"(->|::)\s*$", before):
				continue
			if re.search(r"\bsub\s+$", before):
				continue
			if name in TYPO_MAP:
				message = f"Function name '{name}' looks wrong; use '{TYPO_MAP[name]}'"
				issue = {"severity": "ERROR", "message": message, "line": line_num}
				issues.append(issue)
				continue
			if name not in FUNCTION_RULES:
				continue
			args, close_idx = _parse_args(clean, match.end() - 1)
			if args is None or close_idx == -1:
				continue
			rule = FUNCTION_RULES[name]
			arg_count = 0 if args == [] else len(args)
			min_args = int(rule["min"])
			max_args = rule["max"]
			if arg_count == 0 and min_args > 0:
				message = f"{name}() called with no arguments; expected at least {min_args}"
				issue = {
					"severity": str(rule["severity"]),
					"message": message,
					"line": line_num,
				}
				issues.append(issue)
				continue
			if arg_count < min_args:
				message = f"{name}() called with {arg_count} args; expected at least {min_args}"
				issue = {
					"severity": str(rule["severity"]),
					"message": message,
					"line": line_num,
				}
				issues.append(issue)
				continue
			if isinstance(max_args, int) and arg_count > max_args:
				message = f"{name}() called with {arg_count} args; expected {max_args}"
				issue = {
					"severity": str(rule["severity"]),
					"message": message,
					"line": line_num,
				}
				issues.append(issue)
				continue
			if any(arg.strip() == "" for arg in args):
				message = f"{name}() has an empty argument"
				issue = {
					"severity": str(rule["severity"]),
					"message": message,
					"line": line_num,
				}
				issues.append(issue)

	return issues
