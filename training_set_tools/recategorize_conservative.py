#!/usr/bin/env python3
"""
More conservative categorization - only flag obvious typos.
"""
import os
import re

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
		# Look for ($var, ...) = or (..., $var) =
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
		# Look for $var[...] =
		pattern = rf'\${var_name}\[[^\]]+\]\s*='
		return bool(re.search(pattern, content))
	except Exception:
		return False

#============================================
def is_likely_real_bug(issue: dict, file_path: str) -> bool | str:
	"""
	Conservative check - categorize issues.

	Returns:
		True - real bug
		False - false positive
		'legacy' - old-style code that works but should be updated
	"""
	plugin = issue.get('plugin', '')
	message = str(issue.get('message', ''))

	# Missing answer spec - could be old-style or real bug
	if plugin == 'pgml_blanks' and 'missing answer spec' in message:
		# Check for old-style ANS() - this is legacy, not a bug
		if check_for_ans_call(file_path):
			return 'legacy'  # Old-style ANS() call
		return True  # No ANS() call, likely a real bug

	# Document/structure issues are real
	if plugin in ['document_pairs', 'block_markers']:
		return True

	# Variable assignment issues need deeper check
	if plugin == 'pgml_blank_assignments':
		var_match = re.search(r'\$(\w+)', message)
		if not var_match:
			return False

		var_name = var_match.group(1)

		# Common autovivified array names
		if var_name in ['last', 'pair', 'sum', 'disp', 'closedTex']:
			return False

		# Statistical variables from five_point_summary
		if var_name in ['min', 'max', 'median', 'Q1', 'Q3']:
			if check_for_list_assignment(file_path, var_name):
				return False

		# Check for array element assignment
		if check_for_array_element_assignment(file_path, var_name):
			return False

		# Check for list assignment
		if check_for_list_assignment(file_path, var_name):
			return False

		# Variables in complex constructs
		if var_name in ['nFact', 'kFact', 'nkFact', 'pascal', 'init', 'ratio', 'sn']:
			if check_for_array_element_assignment(file_path, var_name):
				return False

		# Only flag as bug if it looks like a simple typo
		# Common typo: answer vs ans
		if var_name in ['ans'] and os.path.exists(file_path):
			try:
				with open(file_path, 'r') as f:
					content = f.read()
				if '$answer' in content:
					return True  # Likely typo
			except:
				pass

		# Conservative: assume it's NOT a bug unless proven otherwise
		return False

	return False

#============================================
def main():
	"""Main function."""
	# Read known issues
	real_bugs = []
	likely_false_positives = []
	legacy_code = []

	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())

	with open(os.path.join(OUTPUT_DIR, 'known_issues_pg.txt'), 'r') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('#'):
				continue

			# Parse: path:line [plugin] message
			if ':' not in line:
				continue

			file_path = line.split(':')[0]
			if not os.path.exists(file_path):
				continue

			# Re-run linter on this file
			issues = pgml_lint.engine.lint_file(file_path, block_rules, macro_rules, plugins)

			for issue in issues:
				plugin = issue.get('plugin', '')
				message = issue.get('message', '')
				line_no = issue.get('line', '?')

				entry = f"{file_path}:{line_no} [{plugin}] {message}"

				result = is_likely_real_bug(issue, file_path)
				if result is True:
					real_bugs.append(entry)
				elif result == 'legacy':
					legacy_code.append(entry)
				else:
					likely_false_positives.append(entry)

	# Write conservative results
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	with open(os.path.join(OUTPUT_DIR, 'confirmed_bugs_pg.txt'), 'w') as f:
		f.write("# Confirmed bugs - high confidence these are real errors\n")
		f.write("# These have been validated to exclude false positives\n\n")
		for entry in sorted(set(real_bugs)):
			f.write(entry + '\n')

	with open(os.path.join(OUTPUT_DIR, 'mixed_legacy_pg.txt'), 'w') as f:
		f.write("# Legacy PGML - old-style code that works but should be modernized\n")
		f.write("# These use old-style ANS() calls instead of inline answer specs\n")
		f.write("#\n")
		f.write("# Old style: [____] in PGML, then ANS($ans->cmp()) after\n")
		f.write("# Modern:    [____]{$ans} inline\n\n")
		for entry in sorted(set(legacy_code)):
			f.write(entry + '\n')

	with open(os.path.join(OUTPUT_DIR, 'likely_false_positives_pg.txt'), 'w') as f:
		f.write("# Likely false positives - code that works but parser doesn't understand\n")
		f.write("# Includes: list assignments, array element assignments\n")
		f.write("#\n")
		f.write("# Examples of valid Perl our parser misses:\n")
		f.write("# - List assignments: ($a, $b) = func()\n")
		f.write("# - Array element assignment: $arr[0] = value (creates @arr)\n")
		f.write("# - Complex loops and dynamic variables\n\n")
		for entry in sorted(set(likely_false_positives)):
			f.write(entry + '\n')

	print(f"Confirmed bugs: {len(set(real_bugs))}")
	print(f"Legacy code (old-style ANS): {len(set(legacy_code))}")
	print(f"Likely false positives: {len(set(likely_false_positives))}")

#============================================
if __name__ == '__main__':
	main()
