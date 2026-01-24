#!/usr/bin/env python3
"""
Categorize PGML lint issues into known bugs, mixed legacy, and other issues.
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
def parse_args():
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Categorize PGML lint issues"
	)
	parser.add_argument(
		'files', nargs='+',
		help='Files to categorize'
	)
	args = parser.parse_args()
	return args

#============================================
def check_file_content(file_path: str) -> dict:
	"""
	Check file content for legacy PG patterns.
	"""
	info = {
		'has_begin_text': False,
		'has_begin_pgml': False,
		'has_ans_rule': False,
		'has_pgml_blanks': False,
	}

	try:
		with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
			content = f.read()

		info['has_begin_text'] = bool(re.search(r'BEGIN_TEXT', content))
		info['has_begin_pgml'] = bool(re.search(r'BEGIN_PGML', content))
		info['has_ans_rule'] = bool(re.search(r'ans_rule|ANS_RULE', content))
		info['has_pgml_blanks'] = bool(re.search(r'\[\s*_+\s*\]', content))

	except Exception:
		pass

	return info

#============================================
def categorize_issue(issue: dict, file_path: str, file_info: dict) -> str:
	"""
	Categorize an issue into known_bugs, mixed_legacy, or other.
	"""
	plugin = issue.get('plugin', '')
	message = str(issue.get('message', ''))

	# Check for mixed legacy PG
	if file_info['has_begin_text'] and file_info['has_begin_pgml']:
		return 'mixed_legacy'

	if file_info['has_ans_rule'] and file_info['has_pgml_blanks']:
		return 'mixed_legacy'

	# Blank assignment issues - could be real bugs or autovivification
	if plugin == 'pgml_blank_assignments':
		# Extract variable name from message
		var_match = re.search(r'\$(\w+)', message)
		if var_match:
			var_name = var_match.group(1)
			# Common autovivified arrays
			if var_name in ['last', 'pair', 'sum', 'disp', 'closedTex']:
				return 'other'  # Likely autovivified array
			else:
				return 'known_bugs'  # Likely typo

	# Missing answer spec is a real bug
	if plugin == 'pgml_blanks' and 'missing answer spec' in message:
		return 'known_bugs'

	# Document pairs mismatch
	if plugin == 'document_pairs':
		return 'known_bugs'

	# Block markers (unmatched BEGIN/END)
	if plugin == 'block_markers':
		return 'known_bugs'

	# Macro issues - check if it's a false positive
	if plugin == 'macro_rules':
		# PGML.pl automatically loads niceTables.pl
		if 'nicetables.pl' in message.lower() and file_info.get('has_begin_pgml'):
			return 'other'  # False positive - PGML loads it
		return 'known_bugs'  # Real macro issue

	# Default to other
	return 'other'

#============================================
def main():
	"""
	Main function.
	"""
	args = parse_args()

	# Set up linter
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())

	known_bugs = []
	mixed_legacy = []
	other_issues = []

	for file_path in args.files:
		if not os.path.exists(file_path):
			print(f"File not found: {file_path}")
			continue

		# Check file content
		file_info = check_file_content(file_path)

		# Run linter
		issues = pgml_lint.engine.lint_file(
			file_path,
			block_rules,
			macro_rules,
			plugins
		)

		if not issues:
			continue

		# Categorize each issue
		for issue in issues:
			category = categorize_issue(issue, file_path, file_info)
			plugin = issue.get('plugin', 'unknown')
			message = issue.get('message', '')
			line = issue.get('line', '?')

			entry = f"{file_path}:{line} [{plugin}] {message}"

			if category == 'known_bugs':
				known_bugs.append(entry)
			elif category == 'mixed_legacy':
				mixed_legacy.append(entry)
			else:
				other_issues.append(entry)

	# Write results
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	with open(os.path.join(OUTPUT_DIR, 'known_issues_pg.txt'), 'w') as f:
		f.write("# Known bugs in PGML files\n")
		f.write("# These are real errors that should be fixed\n\n")
		for entry in sorted(known_bugs):
			f.write(entry + '\n')

	with open(os.path.join(OUTPUT_DIR, 'mixed_legacy_pg.txt'), 'w') as f:
		f.write("# Files mixing legacy PG and PGML\n")
		f.write("# These files use both BEGIN_TEXT and BEGIN_PGML, or ans_rule() with PGML blanks\n\n")
		for entry in sorted(set(mixed_legacy)):
			f.write(entry + '\n')

	with open(os.path.join(OUTPUT_DIR, 'other_issues_pg.txt'), 'w') as f:
		f.write("# Other issues - autovivified arrays, macros, etc.\n")
		f.write("# These may be false positives or non-critical issues\n\n")
		for entry in sorted(other_issues):
			f.write(entry + '\n')

	print(f"Categorized {len(known_bugs)} known bugs")
	print(f"Categorized {len(mixed_legacy)} mixed legacy issues")
	print(f"Categorized {len(other_issues)} other issues")

#============================================
if __name__ == '__main__':
	main()
