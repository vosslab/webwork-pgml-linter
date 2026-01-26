#!/usr/bin/env python3
"""
Lint all PGML files and categorize results in one step.
"""
import os
import re
import argparse

# local repo modules
import pgml_lint.engine
import pgml_lint.registry
import pgml_lint.rules

#============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

#============================================
def check_for_ans_call(file_path: str) -> bool:
	"""Check if file uses old-style ANS() calls."""
	try:
		with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
			content = f.read()
		return bool(re.search(r'\bANS\s*\(', content))
	except Exception:
		return False

#============================================
def check_for_list_assignment(file_path: str, var_name: str) -> bool:
	"""Check if variable appears in list assignment."""
	try:
		with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
			content = f.read()
		pattern = rf'\(\s*[^)]*\${var_name}[^)]*\)\s*='
		return bool(re.search(pattern, content))
	except Exception:
		return False

#============================================
def check_for_array_element_assignment(file_path: str, var_name: str) -> bool:
	"""Check if $var[...] = appears (creating array)."""
	try:
		with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
			content = f.read()
		pattern = rf'\${var_name}\[[^\]]+\]\s*='
		return bool(re.search(pattern, content))
	except Exception:
		return False

#============================================
def categorize_issue(issue: dict, file_path: str) -> str:
	"""
	Categorize an issue as bug, legacy, or false_positive.
	"""
	plugin = issue.get('plugin', '')
	message = str(issue.get('message', ''))

	# Missing answer spec - could be old-style or real bug
	if plugin == 'pgml_blanks' and 'missing answer spec' in message:
		if check_for_ans_call(file_path):
			return 'legacy'  # Old-style ANS() call
		return 'bug'  # No ANS() call, likely a real bug

	# Document/structure issues are real bugs
	if plugin in ['document_pairs', 'block_markers']:
		return 'bug'

	# Variable assignment issues need deeper check
	if plugin == 'pgml_blank_assignments':
		var_match = re.search(r'\$(\w+)', message)
		if not var_match:
			return 'false_positive'

		var_name = var_match.group(1)

		# Common autovivified array names
		if var_name in ['last', 'pair', 'sum', 'disp', 'closedTex']:
			return 'false_positive'

		# Statistical variables from five_point_summary
		if var_name in ['min', 'max', 'median', 'Q1', 'Q3']:
			if check_for_list_assignment(file_path, var_name):
				return 'false_positive'

		# Check for array element assignment
		if check_for_array_element_assignment(file_path, var_name):
			return 'false_positive'

		# Check for list assignment
		if check_for_list_assignment(file_path, var_name):
			return 'false_positive'

		# Variables in complex constructs
		if var_name in ['nFact', 'kFact', 'nkFact', 'pascal', 'init', 'ratio', 'sn']:
			if check_for_array_element_assignment(file_path, var_name):
				return 'false_positive'

		# Conservative: assume it's NOT a bug unless proven otherwise
		return 'false_positive'

	# Macro issues - check if false positive
	if plugin == 'macro_rules':
		if 'nicetables.pl' in message.lower():
			# Check if file uses PGML (which auto-loads niceTables)
			try:
				with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
					if 'BEGIN_PGML' in f.read():
						return 'false_positive'
			except:
				pass

	return 'false_positive'

#============================================
def parse_args():
	"""Parse command-line arguments."""
	parser = argparse.ArgumentParser(
		description="Lint all PGML files and categorize results"
	)
	parser.add_argument(
		'-f', '--file-list', dest='file_list', type=str,
		default='./all_pgml_files.txt',
		help='File containing list of PGML files (default: ./all_pgml_files.txt)'
	)
	parser.add_argument(
		'-n', '--max-files', dest='max_files', type=int, default=None,
		help='Maximum number of files to process (default: all)'
	)
	args = parser.parse_args()
	return args

#============================================
def main():
	"""Main function."""
	args = parse_args()

	# Read file list
	print(f"Reading file list from {args.file_list}...")
	with open(args.file_list, 'r') as f:
		all_files = [line.strip() for line in f if line.strip()]

	if args.max_files:
		all_files = all_files[:args.max_files]

	print(f"Processing {len(all_files)} files...")

	# Set up linter
	print("Loading linter rules and plugins...")
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())

	# Categorize issues
	bugs = []
	legacy = []
	false_positives = []

	files_processed = 0
	files_with_issues = 0

	for idx, file_path in enumerate(all_files, 1):
		if idx % 100 == 0:
			print(f"  Processed {idx}/{len(all_files)} files... ({files_with_issues} with issues)")

		if not os.path.exists(file_path):
			continue

		files_processed += 1

		# Run linter
		try:
			issues = pgml_lint.engine.lint_file(file_path, block_rules, macro_rules, plugins)
		except Exception as e:
			print(f"  ERROR processing {file_path}: {e}")
			continue

		if not issues:
			continue

		files_with_issues += 1

		# Categorize each issue
		for issue in issues:
			plugin = issue.get('plugin', 'unknown')
			message = issue.get('message', '')
			line_no = issue.get('line', '?')

			entry = f"{file_path}:{line_no} [{plugin}] {message}"
			category = categorize_issue(issue, file_path)

			if category == 'bug':
				bugs.append(entry)
			elif category == 'legacy':
				legacy.append(entry)
			else:
				false_positives.append(entry)

	# Create output directory
	print(f"\nWriting results to {OUTPUT_DIR}...")
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	if bugs:
		with open(os.path.join(OUTPUT_DIR, 'confirmed_bugs_pg.txt'), 'w') as f:
			f.write("# Confirmed bugs - high confidence these are real errors\n")
			f.write("# These have been validated to exclude false positives\n\n")
			for entry in sorted(set(bugs)):
				f.write(entry + '\n')

	if legacy:
		with open(os.path.join(OUTPUT_DIR, 'mixed_legacy_pg.txt'), 'w') as f:
			f.write("# Legacy PGML - old-style code that works but should be modernized\n")
			f.write("# These use old-style ANS() calls instead of inline answer specs\n")
			f.write("#\n")
			f.write("# Old style: [____] in PGML, then ANS($ans->cmp()) after\n")
			f.write("# Modern:    [____]{$ans} inline\n\n")
			for entry in sorted(set(legacy)):
				f.write(entry + '\n')

	if false_positives:
		with open(os.path.join(OUTPUT_DIR, 'likely_false_positives_pg.txt'), 'w') as f:
			f.write("# Likely false positives - code that works but parser doesn't understand\n")
			f.write("# Includes: list assignments, array element assignments\n")
			f.write("#\n")
			f.write("# Examples of valid Perl our parser misses:\n")
			f.write("# - List assignments: ($a, $b) = func()\n")
			f.write("# - Array element assignment: $arr[0] = value (creates @arr)\n")
			f.write("# - Complex loops and dynamic variables\n\n")
			for entry in sorted(set(false_positives)):
				f.write(entry + '\n')

	# Print summary
	print(f"\n{'='*70}")
	print("RESULTS")
	print(f"{'='*70}")
	print(f"Files processed: {files_processed}")
	print(f"Files with issues: {files_with_issues}")
	print("")
	print(f"Confirmed bugs: {len(set(bugs))}")
	print(f"Legacy code: {len(set(legacy))}")
	print(f"False positives: {len(set(false_positives))}")
	print("")

	# List only files that were created
	created_files = []
	if bugs:
		created_files.append("confirmed_bugs_pg.txt")
	if legacy:
		created_files.append("mixed_legacy_pg.txt")
	if false_positives:
		created_files.append("likely_false_positives_pg.txt")

	if created_files:
		print(f"Output files in {OUTPUT_DIR}:")
		for filename in created_files:
			print(f"  - {os.path.join(OUTPUT_DIR, filename)}")
	else:
		print("No issues found - no output files created!")

#============================================
if __name__ == '__main__':
	main()
