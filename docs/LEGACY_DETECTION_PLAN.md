# Legacy PG detection plan

Plan for expanding legacy PG detection in the linter while keeping false positives low.

## Purpose

- Identify legacy PG constructs that should be migrated to PGML or MathObjects.
- Define a rollout order for new detectors and tests.
- Keep guidance clear and actionable for problem authors.

## Scope

- Offline detection in `pgml_lint/` plugins.
- PG and PGML sources in training and production repos.
- Warnings and errors that encourage modernization.

## Non-goals

- Auto-fixing source files.
- Rewriting existing content without author review.

## Candidate legacy patterns

- Old answer evaluators: `num_cmp`, `std_num_cmp`, `arith_cmp`, `fun_cmp`,
  `function_cmp`, `str_cmp`, `list_cmp`, `ordered_list_cmp`, `unordered_list_cmp`.
- Legacy blanks with separate evaluation: `ans_rule()` / `answer_rule()` paired
  with `ANS()` or `&ANS`.
- Legacy answer macros: `NAMED_ANS()` and related wrapper macros.
- Legacy text blocks: `BEGIN_TEXT/END_TEXT`, `TEXT()`, and `\{...\}` interpolation.
- String evaluation helpers: `EV2`, `EV3`, and heredoc-based problem statements.
- Legacy solution and hint macros: `SOLUTION(EV3(<<'END'))`, `HINT(EV3(<<'END'))`.
- Layout hacks: `$BR`, manual TeX spacing commands in text blocks.
- Context toggles used as formatting switches: `Context()->texStrings()` and
  `Context()->normalStrings()`.
- Deprecated choice helpers from `PGchoicemacros.pl`:
  - `qa`
  - `invert`
  - `NchooseK`
  - `shuffle`
  - `match_questions_list`
  - `match_questions_list_varbox`
- Deprecated helpers from other macro files:
  - `contextPeriodic.pl` (deprecated: features added to Real and Complex contexts)
  - `parserMultiPart.pl` (deprecated: renamed to `MultiAnswer`)
  - `PG.pl` (deprecated marker present; identify specific targets before linting)
  - `PGfunctionevaluators.pl`: `multivar_function_cmp`
  - `PGnumericevaluators.pl`: `numerical_compare_with_units`, `std_num_str_cmp`
  - `PGtextevaluators.pl`: `mail_answers_to`, `save_answer_to_file`,
    `save_questionnaire_answers_to`, `DUMMY_ANSWER`
  - `tableau.pl` legacy methods (use `Tableau->statevars` and `Tableau->basis`)

## Prioritization rubric

- Impact: does it break modern rendering or cause hidden grading issues?
- Frequency: how common is it in the training set or production content?
- False positives: can we detect it with low ambiguity?
- Migration clarity: do we have a clear PGML replacement to recommend?

## Detection approach

- Use targeted regex checks in new plugins, scoped to block types when possible.
- Reuse parser helpers for block detection and line/column reporting.
- Keep messages short and include one recommended replacement.
- Prefer warnings first; upgrade to errors if risk is high and migration is safe.

## Rollout plan

- Phase 1 (low risk): direct macro names with clear replacements.
- Phase 2 (medium risk): context toggles and heredoc usage.
- Phase 3 (higher risk): text formatting hacks and ambiguous patterns.

## Testing and validation

- Add focused unit tests under `tests/` for each new plugin.
- Add a small curated fixture set to guard against false positives.
- Run a corpus scan and record counts before and after rule changes.

## Reporting

- Summarize new detectors in [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md).
- Add migration examples to [docs/PGML_LINT_EXAMPLES.md](PGML_LINT_EXAMPLES.md).
- Record each detection change in [docs/CHANGELOG.md](CHANGELOG.md).

## Open questions

- Which legacy patterns are acceptable when PGML wrappers are unavailable?
- Should any detections be suppressed for known PG version constraints?
- Do we need per-repo allowlists for rare legacy constructs?
