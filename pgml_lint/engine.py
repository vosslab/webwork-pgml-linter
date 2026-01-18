# Standard Library

# Local modules
import pgml_lint.parser


#============================================


def build_context(
	text: str,
	file_path: str | None,
	block_rules: list[dict[str, str]],
	macro_rules: list[dict[str, object]],
) -> dict[str, object]:
	"""
	Build a shared context dict for plugins.

	Args:
		text: Full file contents.
		file_path: Optional file path.
		block_rules: Block rules.
		macro_rules: Macro rules.

	Returns:
		dict[str, object]: Context dict.
	"""
	newlines = pgml_lint.parser.build_newline_index(text)
	stripped_comments = pgml_lint.parser.strip_comments(text)
	stripped_text = pgml_lint.parser.strip_heredocs(stripped_comments)
	macros_loaded = pgml_lint.parser.extract_loaded_macros(stripped_text)
	assigned_vars = pgml_lint.parser.extract_assigned_vars(stripped_text)
	uses_pgml = pgml_lint.parser.detect_pgml_usage(stripped_text)
	block_marker_issues, pgml_regions = pgml_lint.parser.extract_block_markers(text)
	heredoc_issues, heredoc_regions = pgml_lint.parser.extract_pgml_heredoc_regions(text)
	pgml_regions_all = list(pgml_regions) + list(heredoc_regions)

	context = {
		"file_path": file_path,
		"text": text,
		"newlines": newlines,
		"stripped_comments": stripped_comments,
		"stripped_text": stripped_text,
		"macros_loaded": macros_loaded,
		"assigned_vars": assigned_vars,
		"uses_pgml": uses_pgml or bool(pgml_regions_all),
		"block_rules": block_rules,
		"macro_rules": macro_rules,
		"block_marker_issues": block_marker_issues,
		"pgml_regions": pgml_regions_all,
		"pgml_block_regions": pgml_regions,
		"pgml_heredoc_regions": heredoc_regions,
		"pgml_heredoc_issues": heredoc_issues,
	}
	return context


#============================================


def _sort_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
	"""
	Return issues sorted by line number then message.

	Args:
		issues: Issue list.

	Returns:
		list[dict[str, object]]: Sorted issues.
	"""
	def issue_key(issue: dict[str, object]) -> tuple[int, str]:
		line = issue.get("line")
		if isinstance(line, int):
			return (line, str(issue.get("message", "")))
		return (10**9, str(issue.get("message", "")))

	return sorted(issues, key=issue_key)


#============================================


def run_plugins(
	context: dict[str, object],
	plugins: list[dict[str, object]],
) -> list[dict[str, object]]:
	"""
	Run plugins and return aggregated issues.

	Args:
		context: Shared context dict.
		plugins: Plugin metadata list.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	issues: list[dict[str, object]] = []
	for plugin in plugins:
		plugin_id = str(plugin.get("id"))
		plugin_run = plugin.get("run")
		plugin_issues = plugin_run(context)
		for issue in plugin_issues:
			if issue.get("plugin") is None:
				issue["plugin"] = plugin_id
			issues.append(issue)
	return _sort_issues(issues)


#============================================


def lint_text(
	text: str,
	file_path: str | None,
	block_rules: list[dict[str, str]],
	macro_rules: list[dict[str, object]],
	plugins: list[dict[str, object]],
) -> list[dict[str, object]]:
	"""
	Lint a text blob with configured plugins.

	Args:
		text: File contents.
		file_path: Optional file path.
		block_rules: Block rules.
		macro_rules: Macro rules.
		plugins: Enabled plugins.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	context = build_context(text, file_path, block_rules, macro_rules)
	issues = run_plugins(context, plugins)
	return issues


#============================================


def lint_file(
	file_path: str,
	block_rules: list[dict[str, str]],
	macro_rules: list[dict[str, object]],
	plugins: list[dict[str, object]],
) -> list[dict[str, object]]:
	"""
	Lint a single file.

	Args:
		file_path: Path to file.
		block_rules: Block rules.
		macro_rules: Macro rules.
		plugins: Enabled plugins.

	Returns:
		list[dict[str, object]]: Issue list.
	"""
	with open(file_path, "r", encoding="utf-8") as handle:
		text = handle.read()
	issues = lint_text(text, file_path, block_rules, macro_rules, plugins)
	return issues
