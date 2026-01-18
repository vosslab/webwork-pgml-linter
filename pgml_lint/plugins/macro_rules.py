# Standard Library
import re


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

	should_check_macros = bool(macros_loaded) or re.search(r"\bDOCUMENT\s*\(\s*\)", text)
	if not should_check_macros:
		return issues

	for rule in rules:
		label = str(rule.get("label", ""))
		pattern = str(rule.get("pattern", ""))
		required_macros = [macro.lower() for macro in rule.get("required_macros", [])]
		if re.search(pattern, text) is None:
			continue
		if any(macro in macros_loaded for macro in required_macros):
			continue
		joined_macros = ", ".join(required_macros)
		message = f"{label} used without required macros: {joined_macros}"
		issue = {"severity": "WARNING", "message": message}
		issues.append(issue)

	return issues
