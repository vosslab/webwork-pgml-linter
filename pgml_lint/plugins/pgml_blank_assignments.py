PLUGIN_ID = "pgml_blank_assignments"
PLUGIN_NAME = "PGML blank assignments"
DEFAULT_ENABLED = True


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when PGML blanks reference variables not assigned in the file.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	blank_vars = context.get("pgml_blank_vars")
	assigned_vars = context.get("assigned_vars", set())

	if not blank_vars:
		return issues

	for name in sorted(blank_vars):
		if name in assigned_vars:
			continue
		message = f"PGML blank references ${name} without assignment in file"
		issue = {"severity": "WARNING", "message": message}
		issues.append(issue)

	return issues
