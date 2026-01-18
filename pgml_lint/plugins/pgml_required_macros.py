PLUGIN_ID = "pgml_required_macros"
PLUGIN_NAME = "PGML requires PGML.pl"
DEFAULT_ENABLED = True

PGML_REQUIRED_MACROS = {"pgml.pl"}


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
	"""
	Warn when PGML is used without PGML.pl.

	Args:
		context: Shared lint context.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	uses_pgml = bool(context.get("uses_pgml"))
	macros_loaded = context.get("macros_loaded", set())
	if not uses_pgml:
		return issues
	if PGML_REQUIRED_MACROS.issubset(macros_loaded):
		return issues
	missing = ", ".join(sorted(PGML_REQUIRED_MACROS))
	message = f"PGML used without required macros: {missing}"
	issue = {"severity": "WARNING", "message": message}
	issues.append(issue)
	return issues
