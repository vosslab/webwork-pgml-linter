# Training Set Tools

Helper scripts for analyzing the `webwork-pgml-opl-training-set` dataset. These are
not part of the core `pgml_lint` package and are intended for dataset-scale linting
and review workflows.

## Prerequisites
- Training set checkout at `OTHER_REPOS-do_not_commit/webwork-pgml-opl-training-set/`.
- A file list at [all_pgml_files.txt](../all_pgml_files.txt), containing one PGML file
  path per line (paths should be absolute or repo-relative).

## Output location
Scripts write results under [training_set_tools/output/](output/). The directory is created
automatically when needed.

## Typical workflow
1) Run the full lint and categorization pass:
   - `python3 training_set_tools/lint_and_categorize_all.py -f all_pgml_files.txt`
2) Summarize results:
   - `python3 training_set_tools/analyze_results.py`
3) Generate per-plugin files for manual review:
   - `python3 training_set_tools/create_bug_type_files.py`
4) Spot-check a random subset:
   - `python3 training_set_tools/test_random_pgml_subset.py -n 50 -f all_pgml_files.txt`

## Script reference
- [lint_and_categorize_all.py](lint_and_categorize_all.py): End-to-end pass over the file list, writing:
  `confirmed_bugs_pg.txt`, `mixed_legacy_pg.txt`, and `likely_false_positives_pg.txt`
  under [training_set_tools/output/](output/).
- [analyze_results.py](analyze_results.py): Reads the output files and prints summaries by plugin, repo,
  and file.
- [create_bug_type_files.py](create_bug_type_files.py): Expands confirmed bugs into per-plugin files and writes
  `false_positives_common_vars.txt` for quick review.
- [test_random_pgml_subset.py](test_random_pgml_subset.py): Runs the linter against a random sample and prints a
  summary of issues.
- [categorize_lint_issues.py](categorize_lint_issues.py): Older one-step categorizer that writes
  `known_issues_pg.txt`, `mixed_legacy_pg.txt`, and `other_issues_pg.txt` into
  [training_set_tools/output/](output/).
- [recategorize_conservative.py](recategorize_conservative.py): Second step of the older flow; reprocesses
  `known_issues_pg.txt` into conservative outputs under [training_set_tools/output/](output/).
- [extract_issue_files.sh](extract_issue_files.sh): Parses [test_results_2000.txt](../test_results_2000.txt) into
  [training_set_tools/output/files_with_issues.txt](output/files_with_issues.txt).
- [examine_issues.sh](examine_issues.sh): Runs the linter against a small, hard-coded list of files for
  manual inspection.
- [test_parser_improvements.py](test_parser_improvements.py): Manual sanity checks for parser improvements (not a
  pytest test module).
