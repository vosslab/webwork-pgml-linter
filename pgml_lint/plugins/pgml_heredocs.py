PLUGIN_ID = "pgml_heredocs"
PLUGIN_NAME = "PGML heredoc terminators"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Report PGML heredoc terminator issues.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	for issue in context.get("pgml_heredoc_issues", []):
		issues.append(issue)
	return issues
