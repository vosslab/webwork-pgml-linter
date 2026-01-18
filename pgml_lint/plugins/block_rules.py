# Standard Library
import re


PLUGIN_ID = "block_rules"
PLUGIN_NAME = "Custom block rule counts"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Apply count-based block rules.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	text = str(context.get("stripped_text", ""))
	rules = context.get("block_rules", [])

	for rule in rules:
		label = str(rule.get("label", ""))
		if label == "DOCUMENT()/ENDDOCUMENT()":
			continue
		start_pattern = str(rule.get("start_pattern", ""))
		end_pattern = str(rule.get("end_pattern", ""))
		if re.search(r"BEGIN_", start_pattern) and re.search(r"END_", end_pattern):
			continue
		start_count = len(re.findall(start_pattern, text))
		end_count = len(re.findall(end_pattern, text))
		if start_count == end_count:
			continue
		if start_count == 0 or end_count == 0:
			message = f"{label} appears only on one side (start={start_count}, end={end_count})"
			issue = {"severity": "WARNING", "message": message}
			issues.append(issue)
			continue
		message = f"{label} counts do not match (start={start_count}, end={end_count})"
		issue = {"severity": "ERROR", "message": message}
		issues.append(issue)

	return issues
