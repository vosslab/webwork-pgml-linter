#!/usr/bin/env python3
"""
Create separate files for each bug type for manual testing.
"""
import os
import re
from collections import defaultdict

#============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

#============================================
def read_and_parse(filename):
	"""Read and parse results file."""
	entries = []
	with open(filename, 'r') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('#'):
				continue

			# Parse: path:line [plugin] message
			parts = line.split('[', 1)
			if len(parts) < 2:
				continue

			file_and_line = parts[0].strip().rstrip(':')
			rest = parts[1]

			plugin_and_msg = rest.split(']', 1)
			if len(plugin_and_msg) < 2:
				continue

			plugin = plugin_and_msg[0].strip()
			message = plugin_and_msg[1].strip()

			# Extract file path
			if ':' in file_and_line:
				file_path = file_and_line.rsplit(':', 1)[0]
				line_no = file_and_line.rsplit(':', 1)[1] if ':' in file_and_line else '?'
			else:
				file_path = file_and_line
				line_no = '?'

			entries.append({
				'file': file_path,
				'line': line_no,
				'plugin': plugin,
				'message': message,
				'full': line
			})
	return entries

#============================================
def main():
	"""Create bug type files."""

	bugs = read_and_parse(os.path.join(OUTPUT_DIR, 'confirmed_bugs_pg.txt'))
	false_pos = read_and_parse(os.path.join(OUTPUT_DIR, 'likely_false_positives_pg.txt'))

	# Group bugs by plugin
	by_plugin = defaultdict(list)
	for bug in bugs:
		by_plugin[bug['plugin']].append(bug)

	# Ensure output directory exists
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	# Write bug type files
	for plugin, items in by_plugin.items():
		filename = os.path.join(OUTPUT_DIR, f"bugs_{plugin}.txt")
		with open(filename, 'w') as f:
			f.write(f"# Confirmed bugs: {plugin}\n")
			f.write(f"# Total: {len(items)} issues\n")
			f.write("#\n")
			f.write("# Test these files in WeBWorK renderer to verify they fail\n")
			f.write("#\n\n")

			# Get unique files
			files = sorted(set(item['file'] for item in items))
			f.write(f"# {len(files)} unique files:\n\n")

			for file_path in files:
				file_issues = [i for i in items if i['file'] == file_path]
				f.write(f"{file_path}\n")
				for issue in file_issues:
					f.write(f"  Line {issue['line']}: {issue['message']}\n")
				f.write("\n")

		print(f"Created {filename} ({len(items)} issues in {len(files)} files)")

	# Create file for common false positive patterns
	var_counts = defaultdict(list)
	for fp in false_pos:
		if fp['plugin'] == 'pgml_blank_assignments':
			var_match = re.search(r'\$(\w+)', fp['message'])
			if var_match:
				var = var_match.group(1)
				var_counts[var].append(fp['file'])

	# Top false positive variables
	with open(os.path.join(OUTPUT_DIR, 'false_positives_common_vars.txt'), 'w') as f:
		f.write("# Common false positive variables\n")
		f.write("# These are variables flagged as missing but likely use list assignment or loops\n")
		f.write("#\n")
		f.write("# Test a few of these in WeBWorK to confirm they render correctly\n\n")

		for var, files in sorted(var_counts.items(), key=lambda x: -len(x[1]))[:20]:
			f.write(f"\n${var}: {len(files)} occurrences\n")
			for file_path in files[:3]:  # Show first 3
				f.write(f"  {file_path}\n")
			if len(files) > 3:
				f.write(f"  ... and {len(files)-3} more\n")

	print(f"Created {os.path.join(OUTPUT_DIR, 'false_positives_common_vars.txt')} (top 20 variables)")

	# Summary
	print(f"\nCreated files in {OUTPUT_DIR} for manual testing:")
	for plugin in by_plugin.keys():
		print(f"  {os.path.join(OUTPUT_DIR, f'bugs_{plugin}.txt')}")
	print(f"  {os.path.join(OUTPUT_DIR, 'false_positives_common_vars.txt')}")

#============================================
if __name__ == '__main__':
	main()
