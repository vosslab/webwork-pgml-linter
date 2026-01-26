#!/usr/bin/env python3
"""
Test the PGML linter on a random subset of files from the training set.
"""
import os
import random
import argparse

# local repo modules
import pgml_lint.engine
import pgml_lint.registry
import pgml_lint.rules

#============================================
def parse_args():
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Test PGML linter on random subset of training files"
	)
	parser.add_argument(
		'-n', '--num-files', dest='num_files', type=int, default=20,
		help='Number of random files to test (default: 20)'
	)
	parser.add_argument(
		'-f', '--file-list', dest='file_list', type=str,
		default='./all_pgml_files.txt',
		help='File containing list of PGML files (default: ./all_pgml_files.txt)'
	)
	parser.add_argument(
		'-v', '--verbose', dest='verbose', action='store_true',
		help='Show detailed output for each file'
	)
	parser.add_argument(
		'-s', '--seed', dest='seed', type=int, default=None,
		help='Random seed for reproducibility'
	)
	args = parser.parse_args()
	return args

#============================================
def read_file_list(file_path: str) -> list:
	"""
	Read the list of PGML files.
	"""
	with open(file_path, 'r') as file:
		lines = file.read().strip().split('\n')
	# Filter out empty lines and ensure files exist
	files = [line.strip() for line in lines if line.strip()]
	return files

#============================================
def test_file(
	file_path: str,
	verbose: bool,
	block_rules: list,
	macro_rules: list,
	plugins: list
) -> dict:
	"""
	Test a single PGML file with the linter.

	Returns a dict with test results.
	"""
	result = {
		'file': file_path,
		'exists': False,
		'issues': [],
		'error': None
	}

	# Check if file exists
	if not os.path.exists(file_path):
		result['error'] = 'File not found'
		return result

	result['exists'] = True

	# Run the linter
	try:
		issues = pgml_lint.engine.lint_file(
			file_path,
			block_rules,
			macro_rules,
			plugins
		)
		result['issues'] = issues
	except Exception as error:
		result['error'] = str(error)

	return result

#============================================
def summarize_results(results: list, verbose: bool):
	"""
	Print a summary of the test results.
	"""
	total_files = len(results)
	files_with_issues = sum(1 for r in results if r['issues'])
	files_with_errors = sum(1 for r in results if r['error'])
	total_issues = sum(len(r['issues']) for r in results)

	print(f"\n{'='*70}")
	print("SUMMARY")
	print(f"{'='*70}")
	print(f"Total files tested: {total_files}")
	print(f"Files with lint issues: {files_with_issues}")
	print(f"Files with errors: {files_with_errors}")
	print(f"Total lint issues found: {total_issues}")
	print()

	# Count issues by plugin
	issue_counts = {}
	for result in results:
		for issue in result['issues']:
			plugin = issue.get('plugin', 'unknown')
			issue_counts[plugin] = issue_counts.get(plugin, 0) + 1

	if issue_counts:
		print("Issues by plugin:")
		for plugin, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
			print(f"  {plugin}: {count}")
		print()

	# Show detailed results if verbose
	if verbose:
		print(f"\n{'='*70}")
		print("DETAILED RESULTS")
		print(f"{'='*70}\n")

		for result in results:
			print(f"File: {result['file']}")

			if result['error']:
				print(f"  ERROR: {result['error']}")
			elif not result['exists']:
				print("  ERROR: File not found")
			elif not result['issues']:
				print("  No issues found")
			else:
				print(f"  Found {len(result['issues'])} issue(s):")
				for issue in result['issues']:
					plugin = issue.get('plugin', 'unknown')
					line = issue.get('line', '?')
					message = issue.get('message', '')
					print(f"    Line {line} [{plugin}]: {message}")
			print()
	else:
		# Show files with issues in non-verbose mode
		files_with_problems = [r for r in results if r['issues'] or r['error']]
		if files_with_problems:
			print(f"\n{'='*70}")
			print(f"FILES WITH ISSUES ({len(files_with_problems)})")
			print(f"{'='*70}\n")

			for result in files_with_problems:
				short_path = result['file'].replace(
					'OTHER_REPOS-do_not_commit/webwork-pgml-opl-training-set/', ''
				)
				issue_count = len(result['issues'])
				if result['error']:
					print(f"  {short_path}: ERROR - {result['error']}")
				else:
					print(f"  {short_path}: {issue_count} issue(s)")

#============================================
def main():
	"""
	Main function to test random PGML files.
	"""
	args = parse_args()

	# Set random seed if provided
	if args.seed is not None:
		random.seed(args.seed)
		print(f"Using random seed: {args.seed}")

	# Read file list
	print(f"Reading file list from {args.file_list}...")
	all_files = read_file_list(args.file_list)
	print(f"Found {len(all_files)} files in list")

	# Select random subset
	num_to_test = min(args.num_files, len(all_files))
	selected_files = random.sample(all_files, num_to_test)
	print(f"Randomly selected {num_to_test} files to test\n")

	# Set up linter rules and plugins
	print("Loading linter rules and plugins...")
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())
	print(f"Loaded {len(plugins)} plugins\n")

	# Test each file
	results = []
	for idx, file_path in enumerate(selected_files, 1):
		short_path = file_path.replace(
			'OTHER_REPOS-do_not_commit/webwork-pgml-opl-training-set/', ''
		)
		print(f"[{idx}/{num_to_test}] Testing {short_path}...", end=' ')

		result = test_file(file_path, args.verbose, block_rules, macro_rules, plugins)
		results.append(result)

		if result['error']:
			print(f"ERROR: {result['error']}")
		else:
			issue_count = len(result['issues'])
			if issue_count == 0:
				print("OK")
			else:
				print(f"{issue_count} issue(s)")

	# Print summary
	summarize_results(results, args.verbose)

#============================================
if __name__ == '__main__':
	main()
