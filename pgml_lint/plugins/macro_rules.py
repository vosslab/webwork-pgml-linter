# Standard Library
import re

# Local modules
import pgml_lint.pg_version

DROPDOWN_COMPAT_RX = re.compile(
	r"defined\s*&DropDown\s*\?\s*DropDown\s*\(\s*@_\s*\)\s*:\s*PopUp\s*\(\s*@_\s*\)",
	re.DOTALL,
)


PLUGIN_ID = "macro_rules"
PLUGIN_NAME = "Macro rule coverage"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Check macro rules when macro coverage is expected.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	macros_loaded = context.get("macros_loaded", set())
	rules = context.get("macro_rules", [])
	pg_version_raw = pgml_lint.pg_version.normalize_pg_version(
		context.get("pg_version")
	)
	dropdown_compat = bool(DROPDOWN_COMPAT_RX.search(text))
	pg_version_tuple = None
	try:
		pg_version_tuple = pgml_lint.pg_version.parse_pg_version(pg_version_raw)
	except ValueError:
		pg_version_tuple = None

	should_check_macros = bool(macros_loaded) or re.search(r"\bDOCUMENT\s*\(\s*\)", text)
	if not should_check_macros:
		return issues

	for rule in rules:
		label = str(rule.get("label", ""))
		pattern = str(rule.get("pattern", ""))
		min_pg_version = rule.get("min_pg_version")
		max_pg_version = rule.get("max_pg_version")
		required_macros = [macro.lower() for macro in rule.get("required_macros", [])]
		if re.search(pattern, text) is None:
			continue
		if pg_version_tuple is not None:
			min_tuple = None
			max_tuple = None
			if min_pg_version is not None:
				try:
					min_tuple = pgml_lint.pg_version.parse_pg_version(
						str(min_pg_version)
					)
				except ValueError:
					min_tuple = None
			if max_pg_version is not None:
				try:
					max_tuple = pgml_lint.pg_version.parse_pg_version(
						str(max_pg_version)
					)
				except ValueError:
					max_tuple = None
			if min_tuple is not None and pg_version_tuple < min_tuple:
				if label == "DropDown" and dropdown_compat:
					continue
				label_text = label if label else "Function"
				message = (
					f"{label_text} requires PG {min_pg_version}+ "
					f"(target is PG {pg_version_raw})"
				)
				issue = {"severity": "WARNING", "message": message}
				issues.append(issue)
				continue
			if max_tuple is not None and pg_version_tuple > max_tuple:
				label_text = label if label else "Function"
				message = (
					f"{label_text} requires PG {max_pg_version} or earlier "
					f"(target is PG {pg_version_raw})"
				)
				issue = {"severity": "WARNING", "message": message}
				issues.append(issue)
				continue
		if any(macro in macros_loaded for macro in required_macros):
			continue
		joined_macros = ", ".join(required_macros)
		message = f"{label} used without required macros: {joined_macros}"
		issue = {"severity": "WARNING", "message": message}
		issues.append(issue)

	return issues
