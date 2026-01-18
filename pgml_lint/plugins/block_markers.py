PLUGIN_ID = "block_markers"
PLUGIN_NAME = "PGML/TEXT/HINT/SOLUTION block pairing"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Report BEGIN/END block pairing issues.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	for issue in context.get("block_marker_issues", []):
		issues.append(issue)
	return issues
