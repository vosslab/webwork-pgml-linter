# Standard Library


SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARNING"


#============================================


def make_issue(
	severity: str,
	message: str,
	line: int | None = None,
	plugin: str | None = None,
) -> dict[str, object]:
	"""
	Create an issue dict.

	Args:
		severity: Severity label.
		message: Issue message.
		line: Optional line number.
		plugin: Optional plugin id.

	Returns:
		dict[str, object]: Issue dict.
	"""
	issue: dict[str, object] = {
		"severity": severity,
		"message": message,
	}
	if line is not None:
		issue["line"] = int(line)
	if plugin is not None:
		issue["plugin"] = plugin
	return issue


#============================================


def summarize_issues(issues: list[dict[str, object]]) -> tuple[int, int]:
	"""
	Summarize issue counts.

	Args:
		issues: Issue list.

	Returns:
		tuple[int, int]: (errors, warnings)
	"""
	errors = len([issue for issue in issues if issue.get("severity") == SEVERITY_ERROR])
	warnings = len([issue for issue in issues if issue.get("severity") != SEVERITY_ERROR])
	return errors, warnings


#============================================


def format_issue(file_path: str, issue: dict[str, object], show_plugin: bool) -> str:
	"""
	Format an issue for display.

	Args:
		file_path: Path to the file.
		issue: Issue dict.
		show_plugin: Whether to include plugin id in output.

	Returns:
		str: Formatted issue line.
	"""
	severity = str(issue.get("severity", SEVERITY_WARNING))
	plugin = issue.get("plugin")
	if show_plugin and plugin:
		severity = f"{severity}({plugin})"
	message = str(issue.get("message", ""))
	line = issue.get("line")
	if isinstance(line, int):
		formatted = f"{file_path}:{line}: {severity}: {message}"
		excerpt = issue.get("excerpt")
		if show_plugin and isinstance(excerpt, str) and excerpt:
			formatted = f"{formatted} | context: {excerpt}"
		return formatted
	formatted = f"{file_path}: {severity}: {message}"
	return formatted
