#!/usr/bin/env python3
"""
Run exploratory PG/PGML cases through the renderer lint API.
"""

# Standard Library
import argparse
import os
import random
import subprocess
import tempfile


RENDERER_SCRIPT_DEFAULT = "/Users/vosslab/nsh/webwork-pg-renderer/script/lint_pg_via_renderer_api.py"


def _wrap_pg(body: str, macros: str | None = None) -> str:
	"""
	Wrap a PGML body in a minimal PG shell.
	"""
	if macros is None:
		macros = "PGstandard.pl', 'PGML.pl"
	text = (
		"DOCUMENT();\n"
		f"loadMacros('{macros}');\n\n"
		"BEGIN_PGML\n"
		f"{body}\n"
		"END_PGML\n\n"
		"ENDDOCUMENT();\n"
	)
	return text


WILD_CASES = {
	"inline_unbalanced": {
		"label": "Unbalanced inline markers",
		"pg": _wrap_pg("[@ 2 + 2"),
	},
	"inline_pgml_wrapper": {
		"label": "PGML wrapper inside inline code",
		"pg": _wrap_pg("[@ \"[<label>]{['div']}{['','']}\" @]*"),
	},
	"inline_braces": {
		"label": "Inline code unbalanced braces",
		"pg": _wrap_pg("[@ my $x = { foo => 1; @]*"),
	},
	"blank_missing_spec": {
		"label": "PGML blank missing spec",
		"pg": _wrap_pg("Answer: [_]"),
	},
	"underscore_unclosed": {
		"label": "Unclosed underscore emphasis",
		"pg": _wrap_pg("This is _italic text."),
	},
	"bracket_unbalanced": {
		"label": "Unbalanced bracket",
		"pg": _wrap_pg("Bracket test [ without close."),
	},
	"raw_div": {
		"label": "Raw div in PGML",
		"pg": _wrap_pg("<div class=\"bad\">Block</div>"),
	},
	"escaped_div": {
		"label": "Escaped div in PGML",
		"pg": _wrap_pg("&lt;div class=\"two-column\"&gt;"),
	},
	"table_tags": {
		"label": "Table tags in PGML",
		"pg": _wrap_pg("<table><tr><td>Cell</td></tr></table>"),
	},
	"raw_span": {
		"label": "Raw span in PGML",
		"pg": _wrap_pg("<span class=\"note\">Span</span>"),
	},
	"tex2jax_ignore": {
		"label": "tex2jax_ignore class",
		"pg": _wrap_pg("<span class=\"tex2jax_ignore\">x</span>"),
	},
	"style_tag": {
		"label": "Style tag in PGML",
		"pg": _wrap_pg("<style>.x { color: red; }</style>"),
	},
	"nested_begin_pgml": {
		"label": "Nested PGML markers",
		"pg": _wrap_pg("[@ \"BEGIN_PGML\" @]*"),
	},
	"ans_rule": {
		"label": "Legacy ans_rule",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');
ans_rule(10);
ENDDOCUMENT();
""",
	},
	"br_variable": {
		"label": "Legacy $BR",
		"pg": """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');
$BR;
ENDDOCUMENT();
""",
	},
	"solution_macro": {
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


def parse_args() -> argparse.Namespace:
	"""
	Parse command-line arguments.
	"""
	parser = argparse.ArgumentParser(
		description="Run exploratory cases through renderer lint."
	)
	parser.add_argument(
		"-r",
		"--renderer-script",
		dest="renderer_script",
		default=RENDERER_SCRIPT_DEFAULT,
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
		dest="seed",
		type=int,
		default=None,
		help="Problem seed (default: random per case).",
	)
	parser.add_argument(
		"--seed-count",
		dest="seed_count",
		type=int,
		default=1,
		help="Number of random seeds per case when --seed is not set.",
	)
	parser.add_argument(
		"-o",
		"--output-format",
		dest="output_format",
		default="classic",
		help="Output format template id (default: classic).",
	)
	parser.add_argument(
		"-c",
		"--case",
		dest="case_ids",
		action="append",
		default=[],
		help="Case id to run (repeatable).",
	)
	parser.add_argument(
		"--list",
		dest="list_cases",
		action="store_true",
		help="List available case ids.",
	)
	parser.add_argument(
		"--report",
		dest="report_path",
		default=None,
		help="Write report to this file.",
	)
	args = parser.parse_args()
	return args


def parse_renderer_output(stdout: str, stderr: str, returncode: int) -> list[str]:
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
	if messages:
		return messages
	if returncode == 0:
		return []
	if stderr:
		return [line for line in stderr.splitlines() if line.strip()]
	return []


def run_renderer(
	renderer_script: str,
	base_url: str,
	seed: int,
	output_format: str,
	text: str,
) -> list[str]:
	"""
	Run lint_pg_via_renderer_api.py for the given PG text.
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
		str(seed),
		"-o",
		output_format,
	]
	result = subprocess.run(cmd, capture_output=True, text=True)
	os.unlink(temp_path)
	return parse_renderer_output(result.stdout, result.stderr, result.returncode)


def format_report(case_id: str, label: str, seed: int, messages: list[str]) -> list[str]:
	"""
	Format a report block for a single run.
	"""
	lines = [
		f"{case_id}: {label}",
		f"seed: {seed}",
		f"messages: {len(messages)}",
	]
	for message in messages:
		lines.append(f"- {message}")
	return lines


def main() -> None:
	"""
	Run the wild probe workflow.
	"""
	args = parse_args()
	if args.list_cases:
		for case_id in sorted(WILD_CASES.keys()):
			print(case_id)
		return

	if not os.path.isfile(args.renderer_script):
		raise FileNotFoundError(f"Renderer script not found: {args.renderer_script}")

	selected = args.case_ids
	if selected:
		case_ids = [cid for cid in selected if cid in WILD_CASES]
	else:
		case_ids = list(WILD_CASES.keys())

	if not case_ids:
		raise RuntimeError("No matching cases selected.")

	report_lines: list[str] = []
	for case_id in case_ids:
		entry = WILD_CASES[case_id]
		text = entry["pg"]
		label = entry["label"]
		seeds: list[int] = []
		if args.seed is not None:
			seeds = [args.seed]
		else:
			for _ in range(max(1, args.seed_count)):
				seeds.append(random.randint(1, 999999))

		for seed in seeds:
			messages = run_renderer(
				args.renderer_script,
				args.base_url,
				seed,
				args.output_format,
				text,
			)
			report_lines.extend(format_report(case_id, label, seed, messages))
			report_lines.append("")

	output = "\n".join(report_lines).rstrip() + "\n"
	if args.report_path:
		with open(args.report_path, "w", encoding="utf-8") as handle:
			handle.write(output)
	else:
		print(output)


if __name__ == "__main__":
	main()
