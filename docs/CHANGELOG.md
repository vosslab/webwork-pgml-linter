# Changelog

## 2026-01-18

- Expand `tools/webwork_pgml_simple_lint.py` with PGML-aware lint checks (blocks, heredocs, blanks, inline markers),
  improved macro/assignment parsing, line-numbered output, and optional JSON summaries.
- Add the `pgml_lint/` plugin framework with built-in PGML lint modules and tests, and refactor the lint CLI to use
  the new plugin registry, enable/disable controls, and JSON summaries.
- Fix MathObjects false positive: recognize that `PGML.pl` loads `MathObjects.pl` internally, so either satisfies
  the MathObjects macro requirement.
- Add math span masking (`[`...`]` and `[:...:+]`) to bracket checker to avoid false positives from LaTeX interval
  notation and other math content.
- Disable `pgml_brackets` plugin by default since plain brackets in PGML text are common (e.g., `(5,10]` in
  documentation).
- Add array/hash variable detection to assignment checker: recognize `@arr =` and `%hash =` patterns to avoid false
  positives when PGML blanks use `$arr[0]` or `$hash{key}`.
- Simplify lint CLI for casual users: just `-i`/`-d` for input, `-v`/`-q` for verbosity. Remove plugin configuration
  options (`--enable`, `--disable`, `--plugin`, `--rules`, `--list-plugins`, `--fail-on-warn`) to make the tool
  work out of the box without configuration.
- Add comprehensive PGML lint documentation:
  - [docs/PGML_LINT.md](docs/PGML_LINT.md): Usage guide and quick start
  - [docs/PGML_LINT_CONCEPTS.md](docs/PGML_LINT_CONCEPTS.md): PGML syntax concepts the linter validates
  - [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md): Reference for all built-in plugins
  - [docs/PGML_LINT_PLUGIN_DEV.md](docs/PGML_LINT_PLUGIN_DEV.md): Guide for writing custom plugins
  - [docs/PGML_LINT_ARCHITECTURE.md](docs/PGML_LINT_ARCHITECTURE.md): Internal architecture for contributors

## 2026-01-17

- Update `README.md` to describe this repo as an AI-training-focused fork and refresh documentation links.
- Add `docs/CORPUS_CURATION.md` and link it from `README.md` to document how the corpus was curated.
- Add `pg_analyze/` (tokenizer + extractors + reports) to produce per-file JSON and TSV summaries for lightweight PG/PGML analysis.
- Improve `pg_analyze/` to handle heredocs during comment stripping, speed up line-number mapping, and make label reasons structured; bump JSON schema to version 2 and add a heredoc comment-stripping test.
- Reorganize `pg_analyze/` modules by merging scan/schema into `main.py`, merging reporting into `report.py`, and merging macro extraction into `extract_evaluators.py` without changing behavior.
- Convert heredoc tokenizer checks to pytest in `tests/test_tokenize_heredoc_comments.py`.
- Fix `pytest tests/` import path for `tests/test_tokenize_heredoc_comments.py` by explicitly adding the repo root to `sys.path`.
- Refactor `pg_analyze` to produce aggregate TSV reports by default (no per-file JSON), with optional `--per-file-tsv` and `--jsonl-out`, and add aggregation tests in `tests/test_pg_analyze_aggregate.py`.
- Update hygiene scripts/tests to skip missing tracked files when running in a working tree with unstaged deletions (`tests/test_indentation.py`, `tests/run_pyflakes.sh`).
- Add `tests/conftest.py` to put the repo root on `sys.path` for pytest.
- Remove per-file output options from `pg_analyze` (no per-file TSV/JSONL) to keep default behavior corpus-scale.
- Add regression tests for common PG/PGML patterns (heredocs, multiline ANS, MultiAnswer, PGML blanks) and count PGML blanks as inputs.
- Pre-strip heredoc bodies before running extractors and record `named_ans_rule(...)` references from evaluator expressions.
- Add aggregate-only "other" analysis reports (breakdown, restricted macro/widget/evaluator counts, PGML blank marker histograms, and small bounded samples) and label `unknown_pgml_blank` when PGML blanks exist but no evaluators/widgets are detected.
- Add cross-tab aggregate reports (type x widget, type x evaluator, widget x evaluator) plus a `coverage.tsv` sanity table.
- Ensure `coverage.tsv` always includes all buckets (including zeros) and extend aggregation tests to cover the cross-tab TSV outputs.
- Make `needs_review.tsv` actionable by bucketing and stratifying samples, and add `needs_review_*_counts.tsv` summaries (bucket/type/macro).
- Write curated bucket file lists under the output directory (`type/`, `widget/`, `evaluator/`) with one path per line for sampling/grepping without per-file JSON or TSV.
- Improve detection of common PGchoicemacros-based widgets/evaluators and add explicit `graph_like` and `essay` labels to reduce the "other" bucket.
- Add evaluator coverage instrumentation reports (`ans_token_hist.tsv`, `evaluator_coverage_reasons.tsv`) plus restricted macro counts and bounded samples to target missing evaluator detection in PGML-heavy files.
- Extract evaluator payloads from PGML blanks (BEGIN/END blocks and PGML heredocs) and add evaluator-source reports (`evaluator_source_counts.tsv`, `pgml_payload_evaluator_counts.tsv`, `type_by_evaluator_source.tsv`) plus an updated `coverage.tsv` that distinguishes ANS vs PGML-derived evaluators.
- Add a bounded diagnostic dump of raw PGML blocks for top `unknown_pgml_blank` signatures (`diagnostics/pgml_blocks_unknown_pgml_blank_top_signatures.txt`) to inspect dominant PGML idioms without per-file output.
- Ensure `pg_analyze` overwrites existing output files and writes outputs into a stable subfolder taxonomy under `-o` (plus an `INDEX.txt` reading order).
- Add simple progress logging and elapsed-time summary to `pg_analyze` runs.
- Add a standard `#` comment header block to TSV outputs and rename select report filenames to emphasize population and unit (directories unchanged).
- Replace ad-hoc samples with signature-based counts and stratified example lists for `unknown_pgml_blank` and `other`.
- Treat PGML blank `*{...}` specs (for example `[____]*{$ans1}`) as grading signals (`source=pgml_star_spec`), add a PGML star-spec evaluator counts report, and cover it with regression tests.
- Refine `pgml_star_spec` evaluator kinds into indirect and expression forms using a lightweight symbol table, add a `matrix_entry` subtype tag (with counts and bucket lists), and rename the dominant unknown signature to `pgml_blank_star_spec_only` when applicable.
- Consolidate most aggregate stats outputs into a few long-format summary tables (`summary/counts_all.tsv`, `summary/cross_tabs_all.tsv`, `summary/histograms_all.tsv`, `summary/macro_counts_segmented.tsv`) and clean up obsolete output files on each run.
- Document the training preference to focus on modern techniques and avoid training AI on legacy techniques (`README.md`, `docs/CORPUS_CURATION.md`).
- Document the intended interaction profile (numeric entry + PGchoice widgets; matching as a rare-flag category) and add `summary/corpus_profile.tsv` plus an `assignment_ordering` type for parserAssignment-based problems.
- Record corpus profile evidence (as of 2026-01-17): `parserMatch.pl=0`, `MatchList=0`, `parserAssignment.pl` present.
- Add a discipline breakdown based on `## DBsubject(...)` metadata, producing `summary/discipline_counts.tsv`, `summary/discipline_subject_counts.tsv`, and `summary/discipline_coverage.tsv` plus per-discipline file lists under `lists/discipline/`.
- Expand DBsubject bucketing to reduce "other" by adding `engineering` and strengthening `chemistry`, plus optional `cs`, `finance`, and `meta` buckets.
- Refine DBsubject bucketing for OPL: split `grade_level` and `meta_noise`/`meta_missing`, expand engineering/physics patterns and typo normalization, fix arithmetic-style DBsubjects as math, and add `discipline_unclassified_subject_counts.tsv` + `discipline_samples.tsv`.
- Add capped content-hint audit outputs (`content_hints/chem_terms_count.tsv`, `content_hints/bio_terms_count.tsv`) for later classifier development without using content scanning for discipline bucketing.
- Add [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md) to summarize the current `output/` corpus reports in a human-readable form.
- Clarify the full-OPL vs PGML-corpus comparison in [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md), link it from `README.md`, and avoid hard-coding an `output/` directory name in [docs/CORPUS_CURATION.md](docs/CORPUS_CURATION.md).
- Expand [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md) with macro/type highlights, selected cross-tab tables, and key histograms beyond the discipline breakdown.
- Extend `pg_analyze` to report DBchapter/DBsection coverage and normalization, path provenance, randomization proxy counts, and exact duplicate counts, and document these comparison stats in [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md).
- Add file-level `widget_kind` coverage counts (distinct per file) alongside widget instance counts, and use those to document widget surface-area differences between full OPL and this PGML corpus.
- Extend [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md) with nonblank DB tag coverage rates and whitespace-stripped duplicate counts.
- Add duplicate-cluster reporting (group-size histograms plus top clusters) and lightweight asset-signal counts to `pg_analyze`, and document these decision-relevant comparisons in [docs/CORPUS_STATS.md](docs/CORPUS_STATS.md).
