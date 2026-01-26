#!/usr/bin/env python3
"""
Compare offline lint plugin results with renderer API lint output.
"""

# Standard Library
import argparse
import os
import subprocess
import sys
import tempfile


def _resolve_repo_root() -> str:
	"""
	Resolve the repo root via git.
	"""
	script_dir = os.path.dirname(os.path.abspath(__file__))
	result = subprocess.run(
		["git", "rev-parse", "--show-toplevel"],
		check=True,
		capture_output=True,
		text=True,
		cwd=script_dir,
	)
	root = result.stdout.strip()
	if not root:
		raise RuntimeError("Unable to resolve REPO_ROOT via git.")
	return root


REPO_ROOT = _resolve_repo_root()
if REPO_ROOT not in sys.path:
	sys.path.insert(0, REPO_ROOT)

# Local modules
import pgml_lint.engine
import pgml_lint.registry
import pgml_lint.rules


PROBE_CASES = {
	"block_markers": {
		"label": "Mismatched PGML block markers",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Mismatched marker.
END_PGML_HINT

ENDDOCUMENT();
""",
	},
	"pgml_heredocs": {
		"label": "Unterminated PGML heredoc",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

PGML::Format(<<'END_PGML');
Hello

ENDDOCUMENT();
""",
	},
	"document_pairs": {
		"label": "Missing ENDDOCUMENT",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');
BEGIN_PGML
Missing enddoc.
END_PGML
""",
	},
	"block_rules": {
		"label": "Custom block rule mismatch",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

FOO_START
No matching end.

ENDDOCUMENT();
""",
	},
	"pgml_required_macros": {
		"label": "PGML used without PGML.pl",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_PGML
Missing PGML macro.
END_PGML

ENDDOCUMENT();
""",
	},
	"macro_rules": {
		"label": "Missing macro requirement",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

Context('Numeric');

BEGIN_PGML
Context should require MathObjects.pl.
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_inline": {
		"label": "Unbalanced inline markers",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ 2 + 2
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_inline_pgml_syntax": {
		"label": "PGML wrapper syntax inside inline code",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ "[<label>]{['div']}{['','']}" @]*
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_inline_braces": {
		"label": "Unbalanced braces in inline code",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
[@ my $x = { foo => 1; @]*
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_blanks": {
		"label": "PGML blank missing spec",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Answer: [_]
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_underscore_emphasis": {
		"label": "Unclosed underscore emphasis",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
This is _italic text.
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_brackets": {
		"label": "Unbalanced brackets",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Bracket test [ without close.
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_blank_assignments": {
		"label": "PGML blank variable without assignment",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Answer: [_]{$missing}
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_label_dot": {
		"label": "Label uses A. dot",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $label = chr(65 + $i) . '. ';

ENDDOCUMENT();
""",
	},
	"pgml_ans_style": {
		"label": "ANS after END_PGML",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Answer: [_______]
END_PGML

ANS($answer->cmp());

ENDDOCUMENT();
""",
	},
	"pgml_text_blocks": {
		"label": "Legacy BEGIN_TEXT",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_TEXT
Legacy text.
END_TEXT

ENDDOCUMENT();
""",
	},
	"pgml_html_in_text": {
		"label": "Raw HTML in PGML text",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
<strong>Bold</strong> text.
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_html_forbidden_tags": {
		"label": "Table tag in PGML",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
<table><tr><td>Cell</td></tr></table>
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_html_div": {
		"label": "Div tag in PGML",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
<div class="bad">Block</div>
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_span_interpolation": {
		"label": "Span HTML not interpolated",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $answers_html = '<span class="ok">Hi</span>';

BEGIN_PGML
No interpolation here.
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_style_string_quotes": {
		"label": "Unescaped quotes in PGML style string",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

%match_data = (
  '[<bond>]{['span', style => 'color: #00b3b3;']}{['','']}' => [
    'H - O - H',
  ],
);

ENDDOCUMENT();
""",
	},
	"pgml_ans_rule": {
		"label": "Legacy ans_rule usage",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

ans_rule(10);

ENDDOCUMENT();
""",
	},
	"pgml_br_variable": {
		"label": "Legacy $BR usage",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$BR;

ENDDOCUMENT();
""",
	},
	"pgml_modes_html_escape": {
		"label": "MODES HTML used with [$var]",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $note = MODES(HTML => '<span>Note</span>', TeX => '');

BEGIN_PGML
[$note]
END_PGML

ENDDOCUMENT();
""",
	},
	"pgml_old_answer_checkers": {
		"label": "Legacy answer checker",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

num_cmp(2);

ENDDOCUMENT();
""",
	},
	"pgml_solution_hint_macros": {
		"label": "Legacy SOLUTION macro",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

SOLUTION(EV3(<<'END_SOLUTION'));
Legacy solution.
END_SOLUTION

ENDDOCUMENT();
""",
	},
}


#============================================


def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Probe offline plugins against renderer API lint output."
	)
	parser.add_argument(
		"-r",
		"--renderer-script",
		dest="renderer_script",
		default="/Users/vosslab/nsh/webwork-pg-renderer/script/lint_pg_via_renderer_api.py",
		help="Path to lint_pg_via_renderer_api.py.",
	)
	parser.add_argument(
		"-b",
		"--base-url",
		dest="base_url",
		default="http://localhost:3000",
		help="Renderer base URL (default: http://localhost:3000).",
	)
	parser.add_argument(
		"-s",
		"--seed",
		dest="problem_seed",
		type=int,
		default=1234,
		help="Problem seed (default: 1234).",
	)
	parser.add_argument(
		"-o",
		"--output-format",
		dest="output_format",
		default="classic",
		help="Output format template id (default: classic).",
	)
	parser.add_argument(
		"-p",
		"--plugin",
		dest="plugin_ids",
		action="append",
		default=[],
		help="Plugin id to probe (repeatable).",
	)
	parser.add_argument(
		"-n",
		"--no-renderer",
		dest="use_renderer",
		action="store_false",
		help="Skip renderer API calls.",
	)
	parser.add_argument(
		"--list",
		dest="list_plugins",
		action="store_true",
		help="List available plugin probe ids.",
	)
	parser.set_defaults(use_renderer=True)
	args = parser.parse_args()
	return args


#============================================


def run_offline_lint(text: str) -> list[dict[str, object]]:
	"""
	Run the full offline lint with default rules.
	"""
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())
	issues = pgml_lint.engine.lint_text(text, None, block_rules, macro_rules, plugins)
	return issues


#============================================


def filter_plugin_issues(issues: list[dict[str, object]], plugin_id: str) -> list[str]:
	"""
	Extract messages for a single plugin.
	"""
	messages: list[str] = []
	for issue in issues:
		if issue.get("plugin") != plugin_id:
			continue
		message = str(issue.get("message", ""))
		line = issue.get("line")
		if isinstance(line, int):
			messages.append(f"line {line}: {message}")
		else:
			messages.append(message)
	return messages


#============================================


def build_custom_rules(plugin_id: str) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
	"""
	Provide custom rules for plugins that need them.
	"""
	block_rules, macro_rules = pgml_lint.rules.load_rules(None)
	if plugin_id == "block_rules":
		block_rules = [
			{
				"label": "FOO_START/FOO_END",
				"start_pattern": r"\bFOO_START\b",
				"end_pattern": r"\bFOO_END\b",
			}
		]
	return block_rules, macro_rules


#============================================


def run_offline_lint_for_plugin(text: str, plugin_id: str) -> list[str]:
	"""
	Run offline lint and return plugin-specific messages.
	"""
	block_rules, macro_rules = build_custom_rules(plugin_id)
	registry = pgml_lint.registry.build_registry()
	plugins = registry.resolve_plugins(set(), set(), set())
	issues = pgml_lint.engine.lint_text(text, None, block_rules, macro_rules, plugins)
	return filter_plugin_issues(issues, plugin_id)


#============================================


def parse_renderer_output(stdout: str) -> list[str]:
	"""
	Extract lint messages from renderer script output.
	"""
	lines = stdout.splitlines()
	if "No lint messages detected." in lines:
		return []
	messages: list[str] = []
	in_messages = False
	for line in lines:
		if line.strip() == "Lint messages:":
			in_messages = True
			continue
		if not in_messages:
			continue
		if line.startswith("- "):
			messages.append(line[2:].strip())
	return messages


#============================================


def run_renderer_lint(
	renderer_script: str,
	base_url: str,
	problem_seed: int,
	output_format: str,
	text: str,
) -> list[str]:
	"""
	Run the renderer lint script and collect messages.
	"""
	with tempfile.NamedTemporaryFile(delete=False, suffix=".pg", mode="w", encoding="utf-8") as handle:
		handle.write(text)
		temp_path = handle.name

	cmd = [
		renderer_script,
		"-i",
		temp_path,
		"-b",
		base_url,
		"-s",
		str(problem_seed),
		"-o",
		output_format,
	]
	result = subprocess.run(cmd, capture_output=True, text=True)
	os.unlink(temp_path)

	messages = parse_renderer_output(result.stdout)
	if messages:
		return messages
	if result.returncode == 0:
		return []
	if result.stderr:
		return [line for line in result.stderr.splitlines() if line.strip()]
	return []


#============================================


def print_report(plugin_id: str, label: str, offline: list[str], renderer: list[str]) -> None:
	"""
	Print a probe report for a plugin.
	"""
	print("")
	print(f"{plugin_id}: {label}")
	print(f"offline issues: {len(offline)}")
	for message in offline:
		print(f"  - {message}")
	print(f"renderer messages: {len(renderer)}")
	for message in renderer:
		print(f"  - {message}")


#============================================


def main() -> None:
	"""
	Run the plugin probe workflow.
	"""
	args = parse_args()
	if args.list_plugins:
		for plugin_id in sorted(PROBE_CASES.keys()):
			print(plugin_id)
		return

	if args.use_renderer and not os.path.isfile(args.renderer_script):
		raise FileNotFoundError(f"Renderer script not found: {args.renderer_script}")

	selected = args.plugin_ids
	if selected:
		probe_ids = [pid for pid in selected if pid in PROBE_CASES]
	else:
		probe_ids = list(PROBE_CASES.keys())

	if not probe_ids:
		raise RuntimeError("No matching plugin probes selected.")

	for plugin_id in probe_ids:
		entry = PROBE_CASES[plugin_id]
		text = entry["pg"]
		label = entry["label"]

		offline_messages = run_offline_lint_for_plugin(text, plugin_id)
		renderer_messages: list[str] = []
		if args.use_renderer:
			renderer_messages = run_renderer_lint(
				args.renderer_script,
				args.base_url,
				args.problem_seed,
				args.output_format,
				text,
			)

		print_report(plugin_id, label, offline_messages, renderer_messages)


if __name__ == "__main__":
	main()
