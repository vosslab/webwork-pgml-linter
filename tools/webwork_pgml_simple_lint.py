#!/usr/bin/env python3

# Standard Library
import argparse
import json
import os
import subprocess
import sys
import tomllib

# Determine repo root and add to path for local imports
REPO_ROOT = subprocess.run(
	["git", "rev-parse", "--show-toplevel"],
	capture_output=True,
	text=True,
	check=True,
).stdout.strip()
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

# Local modules
import pgml_lint.core
import pgml_lint.engine
import pgml_lint.pg_version
import pgml_lint.registry
import pgml_lint.rules


#============================================


def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.

	Returns:
		argparse.Namespace: Parsed arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Check WeBWorK .pg files for common PGML errors.",
	)
	# Input - simple and clear
	input_group = parser.add_mutually_exclusive_group()
	input_group.add_argument(
		"-i",
		"--input",
		dest="input_file",
		help="Check a single .pg file.",
	)
	input_group.add_argument(
		"-d",
		"--directory",
		dest="input_dir",
		help="Check all .pg files in a directory.",
	)
	# Output control - just verbose or quiet
	verbosity_group = parser.add_mutually_exclusive_group()
	verbosity_group.add_argument(
		"-v",
		"--verbose",
		dest="verbose",
		action="store_true",
		help="Show more details.",
	)
	verbosity_group.add_argument(
		"-q",
		"--quiet",
		dest="quiet",
		action="store_true",
		help="Only show problems, no summary.",
	)
	# JSON for scripting (suppress from help - advanced users know about it)
	parser.add_argument(
		"--json",
		dest="json_output",
		action="store_true",
		help=argparse.SUPPRESS,
	)
	parser.add_argument(
		"-p",
		"--pg-version",
		dest="pg_version",
		help="Target PG version for versioned rules (default: 2.17).",
	)
	parser.set_defaults(
		verbose=False,
		quiet=False,
		json_output=False,
	)
	args = parser.parse_args()
	# Default to current directory if no input specified
	if not args.input_file and not args.input_dir:
		args.input_dir = "."
	return args


#============================================


# Default file extension for WeBWorK problem files
DEFAULT_EXTENSIONS = [".pg"]


#============================================


def find_files(input_dir: str, extensions: list[str] = DEFAULT_EXTENSIONS) -> list[str]:
	"""
	Find files under input_dir matching extensions.

	Args:
		input_dir: Root directory to scan.
		extensions: File extensions to include.

	Returns:
		list[str]: Sorted file paths.
	"""
	matches: list[str] = []
	for root, dirs, files in os.walk(input_dir):
		dirs.sort()
		files.sort()
		for filename in files:
			ext = os.path.splitext(filename)[1].lower()
			if ext in extensions:
				matches.append(os.path.join(root, filename))
	paths = sorted(matches)
	return paths


#============================================


def _load_linter_version(repo_root: str) -> str:
	"""
	Load the linter version from pyproject.toml.
	"""
	pyproject_path = os.path.join(repo_root, "pyproject.toml")
	try:
		with open(pyproject_path, "rb") as handle:
			data = tomllib.load(handle)
		version = str(data.get("project", {}).get("version", "")).strip()
		if version:
			return version
	except OSError:
		pass
	except tomllib.TOMLDecodeError:
		pass
	return "unknown"


#============================================


def main() -> None:
	"""
	Run the lint checker.
	"""
	args = parse_args()
	pg_version = pgml_lint.pg_version.normalize_pg_version(args.pg_version)
	linter_version = _load_linter_version(REPO_ROOT)
	print(f"pgml-lint {linter_version}", file=sys.stderr)

	# Use built-in rules and plugins - no configuration needed
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())

	if args.verbose:
		plugin_ids = [str(plugin.get("id")) for plugin in plugins]
		print(f"Active checks: {', '.join(plugin_ids)}")

	issues: list[dict[str, object]] = []
	files_checked: list[str] = []

	if args.input_file:
		files_checked.append(args.input_file)
		file_issues = pgml_lint.engine.lint_file(
			args.input_file,
			block_rules,
			macro_rules,
			plugins,
			pg_version,
		)
		issues.extend(file_issues)
		if not args.json_output:
			for issue in file_issues:
				print(pgml_lint.core.format_issue(args.input_file, issue, args.verbose))
	else:
		files_to_check = find_files(args.input_dir)
		files_checked.extend(files_to_check)
		if args.verbose:
			print(f"Checking {len(files_to_check)} files in {args.input_dir}")
		for file_path in files_to_check:
			file_issues = pgml_lint.engine.lint_file(
				file_path,
				block_rules,
				macro_rules,
				plugins,
				pg_version,
			)
			issues.extend(file_issues)
			if not args.json_output:
				for issue in file_issues:
					print(pgml_lint.core.format_issue(file_path, issue, args.verbose))

	error_count, warn_count = pgml_lint.core.summarize_issues(issues)

	if args.json_output:
		plugin_ids = [str(plugin.get("id")) for plugin in plugins]
		summary = {
			"files_checked": len(files_checked),
			"errors": error_count,
			"warnings": warn_count,
			"issues": issues,
		}
		print(json.dumps(summary, indent=2))
	elif not args.quiet:
		if issues:
			print(f"Found {error_count} errors and {warn_count} warnings.")
		elif args.verbose:
			print(f"No issues found in {len(files_checked)} files.")

	if error_count > 0:
		raise SystemExit(1)


if __name__ == "__main__":
	main()
