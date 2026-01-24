#!/usr/bin/env python3
"""
Analyze the categorized lint results in detail.
"""
import os
import re
from collections import defaultdict

#============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

#============================================
def read_results_file(filename):
	"""Read and parse a results file."""
	entries = []
	with open(filename, 'r') as f:
		for line in f:
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			entries.append(line)
	return entries

#============================================
def parse_entry(entry):
	"""Parse an entry into components."""
	# Format: path:line [plugin] message
	parts = entry.split('[', 1)
	if len(parts) < 2:
		return None

	file_and_line = parts[0].strip().rstrip(':')
	rest = parts[1]

	plugin_and_msg = rest.split(']', 1)
	if len(plugin_and_msg) < 2:
		return None

	plugin = plugin_and_msg[0].strip()
	message = plugin_and_msg[1].strip()

	# Extract file path
	if ':' in file_and_line:
		file_path = file_and_line.rsplit(':', 1)[0]
	else:
		file_path = file_and_line

	return {
		'file': file_path,
		'plugin': plugin,
		'message': message,
		'full': entry
	}

#============================================
def analyze_by_plugin(entries):
	"""Group entries by plugin."""
	by_plugin = defaultdict(list)
	for entry in entries:
		parsed = parse_entry(entry)
		if parsed:
			by_plugin[parsed['plugin']].append(parsed)
	return by_plugin

#============================================
def analyze_by_file(entries):
	"""Group entries by file."""
	by_file = defaultdict(list)
	for entry in entries:
		parsed = parse_entry(entry)
		if parsed:
			by_file[parsed['file']].append(parsed)
	return by_file

#============================================
def get_file_base(file_path):
	"""Get the repository/contributor base."""
	# Extract pattern like "Contrib/CCCS" or "OpenProblemLibrary/PCC"
	parts = file_path.split('/')
	if 'Contrib' in parts:
		idx = parts.index('Contrib')
		if idx + 1 < len(parts):
			return f"Contrib/{parts[idx+1]}"
	elif 'OpenProblemLibrary' in parts:
		idx = parts.index('OpenProblemLibrary')
		if idx + 1 < len(parts):
			return f"OPL/{parts[idx+1]}"
	return "Other"

#============================================
def main():
	"""Main analysis function."""

	print("="*70)
	print("PGML Linter Results Analysis")
	print("="*70)
	print()

	# Read all results from output directory
	bugs = read_results_file(os.path.join(OUTPUT_DIR, 'confirmed_bugs_pg.txt'))
	legacy = read_results_file(os.path.join(OUTPUT_DIR, 'mixed_legacy_pg.txt'))
	false_pos = read_results_file(os.path.join(OUTPUT_DIR, 'likely_false_positives_pg.txt'))

	total_entries = len(bugs) + len(legacy) + len(false_pos)

	print(f"Total issues flagged: {total_entries}")
	print(f"  Confirmed bugs: {len(bugs)}")
	print(f"  Legacy code: {len(legacy)}")
	print(f"  False positives: {len(false_pos)}")
	print()

	# Analyze bugs by plugin
	if bugs:
		print("="*70)
		print("CONFIRMED BUGS - By Plugin")
		print("="*70)
		by_plugin = analyze_by_plugin(bugs)
		for plugin, items in sorted(by_plugin.items(), key=lambda x: -len(x[1])):
			print(f"\n{plugin}: {len(items)} issues")
			for item in items[:5]:  # Show first 5
				file_short = item['file'].split('/')[-1]
				print(f"  - {file_short}: {item['message']}")
			if len(items) > 5:
				print(f"  ... and {len(items)-5} more")
		print()

	# Analyze bugs by repository
	if bugs:
		print("="*70)
		print("CONFIRMED BUGS - By Repository")
		print("="*70)
		by_repo = defaultdict(int)
		for entry in bugs:
			parsed = parse_entry(entry)
			if parsed:
				repo = get_file_base(parsed['file'])
				by_repo[repo] += 1

		for repo, count in sorted(by_repo.items(), key=lambda x: -x[1]):
			print(f"  {repo}: {count} bugs")
		print()

	# Analyze false positives
	if false_pos:
		print("="*70)
		print("FALSE POSITIVES - By Type")
		print("="*70)
		by_plugin = analyze_by_plugin(false_pos)
		for plugin, items in sorted(by_plugin.items(), key=lambda x: -len(x[1])):
			print(f"\n{plugin}: {len(items)} issues")

			# Group by variable name for blank_assignments
			if plugin == 'pgml_blank_assignments':
				var_counts = defaultdict(int)
				for item in items:
					var_match = re.search(r'\$(\w+)', item['message'])
					if var_match:
						var_counts[var_match.group(1)] += 1

				print("  Top variables flagged:")
				for var, count in sorted(var_counts.items(), key=lambda x: -x[1])[:10]:
					print(f"    ${var}: {count} times")
		print()

	# Files with multiple issues
	all_entries = bugs + legacy + false_pos
	by_file = analyze_by_file(all_entries)
	multi_issue_files = {f: issues for f, issues in by_file.items() if len(issues) > 1}

	if multi_issue_files:
		print("="*70)
		print("FILES WITH MULTIPLE ISSUES")
		print("="*70)
		for file_path, issues in sorted(multi_issue_files.items(), key=lambda x: -len(x[1]))[:10]:
			file_short = '/'.join(file_path.split('/')[-3:])
			print(f"\n{file_short}: {len(issues)} issues")
			for issue in issues:
				print(f"  [{issue['plugin']}] {issue['message']}")

		if len(multi_issue_files) > 10:
			print(f"\n... and {len(multi_issue_files)-10} more files with multiple issues")
		print()

	# Summary
	print("="*70)
	print("SUMMARY")
	print("="*70)
	unique_files_with_bugs = len(set(parse_entry(e)['file'] for e in bugs if parse_entry(e)))
	unique_files_with_fps = len(set(parse_entry(e)['file'] for e in false_pos if parse_entry(e)))

	print(f"Files with confirmed bugs: {unique_files_with_bugs}")
	print(f"Files with false positives: {unique_files_with_fps}")
	print(f"Total unique files flagged: {len(by_file)}")
	print()

	if bugs:
		print("Action items:")
		print(f"  1. Fix {len(bugs)} confirmed bugs in {unique_files_with_bugs} files")
		print(f"  2. Review false positives to improve parser")

#============================================
if __name__ == '__main__':
	main()
