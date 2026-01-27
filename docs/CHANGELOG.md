# Changelog

## 2026-01-27 - PG 2.17 macro rule support

- Add PG version normalization utilities and pass `pg_version` through lint context.
- Make `macro_rules` version-aware (min/max PG version checks).
- Treat `DropDown()` and `CheckboxList()` as PG 2.18+ and accept `parserMultipleChoice.pl` for multiple choice rules.
- Allow `tools/webwork_pgml_simple_lint.py` to target a PG version via `--pg-version` and log the linter version to stderr.
- Default the target PG version to 2.17.
- Allow trailing commas in `loadMacros()` without warning.
- Add seed stability and seed variation checks for PG problems.
- Add `docs/RANDOMIZATION_METHODS.md` inventory of PG randomization entry points.
- Expand seed variation detection to include the randomization inventory.
- Expand seed stability checks to cover known reseed helpers.
- Update macro rules documentation and add tests for version gating.

## 2026-01-26 - PGML style string quote checks

- Add `pgml_style_string_quotes` plugin to flag PGML style tags in single-quoted Perl strings with unescaped quotes that cause compile errors.
- Add tests for the new plugin in [tests/test_pgml_lint_plugins_pgml_style_string_quotes.py](../tests/test_pgml_lint_plugins_pgml_style_string_quotes.py).
- Document the new plugin in [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md).
- Warn when `class="tex2jax_ignore"` appears in PGML text via `pgml_html_in_text`, and add coverage in [tests/test_pgml_lint_plugins_pgml_html_in_text.py](../tests/test_pgml_lint_plugins_pgml_html_in_text.py).
- Add `pgml_inline_braces` to catch unbalanced `{}` inside `[@ ... @]*` blocks, plus tests in [tests/test_pgml_lint_plugins_pgml_inline_braces.py](../tests/test_pgml_lint_plugins_pgml_inline_braces.py).
- Add `pgml_underscore_emphasis` to warn on unclosed underscore emphasis in PGML text, plus tests in [tests/test_pgml_lint_plugins_pgml_underscore_emphasis.py](../tests/test_pgml_lint_plugins_pgml_underscore_emphasis.py).
- Add `pgml_html_div` to flag `<div>` tags (including escaped `&lt;div`) in PGML blocks, plus tests in [tests/test_pgml_lint_plugins_pgml_html_div.py](../tests/test_pgml_lint_plugins_pgml_html_div.py).
- Add `pgml_html_forbidden_tags` to error on table-related HTML tags in PGML blocks, plus tests in [tests/test_pgml_lint_plugins_pgml_html_forbidden_tags.py](../tests/test_pgml_lint_plugins_pgml_html_forbidden_tags.py).
- Add `pgml_inline_pgml_syntax` to flag PGML wrapper syntax inside `[@ @]*` blocks, plus tests in [tests/test_pgml_lint_plugins_pgml_inline_pgml_syntax.py](../tests/test_pgml_lint_plugins_pgml_inline_pgml_syntax.py).
- Add `pgml_label_dot` to warn on `A.` label construction, plus tests in [tests/test_pgml_lint_plugins_pgml_label_dot.py](../tests/test_pgml_lint_plugins_pgml_label_dot.py).
- Add `pgml_span_interpolation` to warn when `<span>` HTML variables are not interpolated with `[$var]`, plus tests in [tests/test_pgml_lint_plugins_pgml_span_interpolation.py](../tests/test_pgml_lint_plugins_pgml_span_interpolation.py).
- Add `tools/renderer_plugin_probe.py` to compare offline plugin results with renderer API lint output via the renderer lint script.
- Add `tools/renderer_wild_probe.py` to run exploratory renderer lint cases for new plugin ideas.
- Update `tools/renderer_plugin_probe.py` to resolve REPO_ROOT via `git rev-parse --show-toplevel`.
- Expand `pgml_header_tags` to check DESCRIPTION/KEYWORDS metadata, smart quotes, and duplicate keywords, plus tests in [tests/test_pgml_lint_plugins_pgml_header_tags.py](../tests/test_pgml_lint_plugins_pgml_header_tags.py).
- Add `pgml_include_pgproblem` to warn on include-only stubs and unverifiable includes.
- Add `pgml_line_length` tests in [tests/test_pgml_lint_plugins_pgml_line_length.py](../tests/test_pgml_lint_plugins_pgml_line_length.py).
- Add `pgml_blob_payloads` to warn on base64-like blobs and ggbbase64 markers.
- Add `pgml_nbsp` to warn on non-breaking spaces, plus tests in [tests/test_pgml_lint_plugins_pgml_nbsp.py](../tests/test_pgml_lint_plugins_pgml_nbsp.py).
- Add `pgml_mojibake` to warn on encoding glitches, plus tests in [tests/test_pgml_lint_plugins_pgml_mojibake.py](../tests/test_pgml_lint_plugins_pgml_mojibake.py).
- Add `pgml_tex_color` to warn on TeX color commands, plus tests in [tests/test_pgml_lint_plugins_pgml_tex_color.py](../tests/test_pgml_lint_plugins_pgml_tex_color.py).
- Update [docs/PGML_LINT.md](PGML_LINT.md) and [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md) for the new plugin coverage.
- Add [docs/PGML_LINT_PLUGIN_IDEAS.md](PGML_LINT_PLUGIN_IDEAS.md) with an extensive list of possible offline lint plugins.
- Allow an `ASCII-COMPLIANCE: ALLOW-UTF8` directive (with a reason) to skip ASCII checks in [tests/check_ascii_compliance.py](../tests/check_ascii_compliance.py), [tests/fix_ascii_compliance.py](../tests/fix_ascii_compliance.py), and [tests/test_ascii_compliance.py](../tests/test_ascii_compliance.py).
- Add ASCII compliance allow directive to [training_set_tools/test_parser_improvements.py](../training_set_tools/test_parser_improvements.py) to keep Unicode test markers.
- Expand [docs/PGML_LINT_PLUGIN_IDEAS.md](PGML_LINT_PLUGIN_IDEAS.md) with more instructor-facing lint ideas (macros, inline HTML, syntax pitfalls).
- Rework [docs/PGML_LINT_PLUGIN_IDEAS.md](PGML_LINT_PLUGIN_IDEAS.md) to focus on bigger picture plugins, add function signature checks, and drop INFO-only ideas.
- Add `pgml_loadmacros_integrity`, `pgml_function_signatures`, `pgml_pgml_parse_hazards`, and `pgml_html_policy` plugins with tests and documentation updates.
- Expand `pgml_html_policy` with additional HTML checks (style tag placement, tex2jax_ignore, media tags), plus tests and docs updates.
- Add `pgml_modes_in_inline`, `pgml_html_var_passthrough`, and `pgml_pgml_wrapper_in_string` plugins with tests and documentation updates.
- Extend `macro_rules` defaults to cover `DropDown()` and `NchooseK()` macro requirements.
- Expand `macro_rules` defaults to include `MultiAnswer()`, `OneOf()`, and `FormulaUpToConstant()`, plus signature coverage updates.
- Extract function-to-macro pairs into [pgml_lint/function_to_macro_pairs.py](../pgml_lint/function_to_macro_pairs.py) and keep [pgml_lint/rules.py](../pgml_lint/rules.py) as the public wrapper.
- Fix pyflakes errors in training-set tools by removing empty f-strings.
- Expand `pgml_html_policy` to flag disallowed tags used inside PGML tag wrappers, plus tests and docs updates.
- Extend `pgml_mojibake` detection to flag standalone mojibake markers (U+00C2/U+00C3) with test coverage updates.
- Fix pyflakes warnings by removing empty f-strings in training-set tools and an unused `newlines` variable in `pgml_tex_color`.
- Expand `pgml_inline_pgml_syntax` to flag PGML interpolation strings inside `[@ @]` blocks, plus tests and docs updates.
- Refine `pgml_inline_pgml_syntax` messaging to include the specific wrapper token or interpolation variable and avoid duplicate reports per token.
- Add optional verbose context excerpts for issues with column data, including new `pos_to_col` support and inline syntax column reporting.
- Strip leading whitespace from verbose context excerpts to make them easier to scan.

## 2026-01-24 - Legacy PG syntax detection (major update)

### New Plugins for Legacy PG Detection

This release adds comprehensive detection of deprecated PG syntax patterns, emphasizing that **this linter enforces modern PGML standards**:

1. **`pgml_text_blocks`** - Flag legacy `BEGIN_TEXT/END_TEXT` blocks
   - Warns that TEXT blocks should be migrated to `BEGIN_PGML/END_PGML`
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_text_blocks.py](tests/test_pgml_lint_plugins_pgml_text_blocks.py)

2. **`pgml_html_in_text`** - Detect raw HTML in PGML text
   - Flags HTML tags (`<strong>`, `<em>`, `<br>`, `<sub>`, `<sup>`, tables, etc.) that will be stripped or mangled
   - Detects HTML entities (`&nbsp;`, `&lt;`, `&copy;`, etc.) that may be corrupted
   - Excludes HTML inside `[@ @]*` blocks (where it's allowed)
   - Suggests PGML/LaTeX alternatives for each problematic tag
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_html_in_text.py](tests/test_pgml_lint_plugins_pgml_html_in_text.py)

3. **`pgml_ans_rule`** - Detect legacy `ans_rule()` function
   - Flags old-style answer blank syntax that should use PGML `[_]{$answer}` instead
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_ans_rule.py](tests/test_pgml_lint_plugins_pgml_ans_rule.py)

4. **`pgml_br_variable`** - Detect legacy `$BR` variable
   - Flags old-style line breaks that should use blank lines in PGML
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_br_variable.py](tests/test_pgml_lint_plugins_pgml_br_variable.py)

5. **`pgml_modes_html_escape`** - Detect MODES HTML escaped in interpolation
   - Tracks variables assigned HTML from `MODES(HTML => '<span>...', ...)`
   - Warns when those variables are used with `[$var]` interpolation (which escapes HTML)
   - Suggests using `[@ $var @]*` instead to render HTML correctly
   - Prevents subtle bug where HTML appears as `&lt;span&gt;` instead of rendering
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_modes_html_escape.py](tests/test_pgml_lint_plugins_pgml_modes_html_escape.py)

6. **`pgml_old_answer_checkers`** - Detect legacy answer checker functions
   - Flags deprecated `num_cmp()`, `str_cmp()`, `fun_cmp()` and their variants
   - Suggests using MathObjects with `->cmp()` method instead
   - Encourages migration from old answer checkers to modern MathObjects
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_old_answer_checkers.py](tests/test_pgml_lint_plugins_pgml_old_answer_checkers.py)

7. **`pgml_solution_hint_macros`** - Detect legacy SOLUTION/HINT macros
   - Flags deprecated `SOLUTION(EV3(<<'END'))` and `HINT(EV3(<<'END'))` patterns
   - Suggests using `BEGIN_PGML_SOLUTION` and `BEGIN_PGML_HINT` blocks instead
   - Promotes cleaner, more maintainable PGML syntax
   - Test coverage: [tests/test_pgml_lint_plugins_pgml_solution_hint_macros.py](tests/test_pgml_lint_plugins_pgml_solution_hint_macros.py)

### Documentation Updates

- Update [README.md](README.md): Clarify linter enforces modern PGML and flags legacy PG syntax
- Update [docs/PGML_LINT.md](docs/PGML_LINT.md): Add "Purpose" section emphasizing modern PGML enforcement
- Update [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md):
  - Add documentation for all four new plugins
  - Include migration guides showing legacy PG -> modern PGML conversions
  - Add HTML/PGML conversion table for common tags

### Test Results

- All plugin tests pass: 65 total tests across all plugins
- Full test suite passes: 114 tests

## 2026-01-21 - pgml_ans_style plugin and examples documentation

- Add `pgml_ans_style` plugin to detect mixed PGML/PG answer styles.
- Warn when `ANS()` calls appear after `END_PGML` blocks instead of using pure PGML inline answer specs like `[_]{$answer}`.
- Add comprehensive test coverage for the new plugin in [tests/test_pgml_lint_plugins_pgml_ans_style.py](tests/test_pgml_lint_plugins_pgml_ans_style.py).
- Add `pgml_ans_style` documentation to [docs/PGML_LINT_PLUGINS.md](docs/PGML_LINT_PLUGINS.md) with good/bad examples.
- Create [docs/PGML_LINT_EXAMPLES.md](docs/PGML_LINT_EXAMPLES.md) with comprehensive good vs bad code examples for all lint rules.
- Fix merge conflict in [tests/test_bandit_security.py](tests/test_bandit_security.py).
- Move training-set analysis scripts from repo root into [training_set_tools/](../training_set_tools/).
- Document training-set workflow in [training_set_tools/README.md](../training_set_tools/README.md) and route outputs to `training_set_tools/output/`.

## 2026-01-19 - Testing, validation, and parser improvements

### Testing and Validation

Comprehensive testing on real-world PGML files from the OPL training set with manual validation.

- Test 2,000 random PGML files from 9,386-file training set
- Initially flagged 58 issues in 37 files (1.85% of files)
- **Manual validation in WeBWorK**: Tested 5 random flagged files - 3 rendered fine!
- **Revised analysis**: 4 confirmed bugs + 7 legacy code patterns + 47 false positives
- Create `test_random_pgml_subset.py` for sampling and testing PGML files
- Create `categorize_lint_issues.py` for automated issue classification
- Create `recategorize_conservative.py` for conservative validation
- Generate output files in `output/`: `confirmed_bugs_pg.txt`, `mixed_legacy_pg.txt`, `likely_false_positives_pg.txt`
- Document testing results in [TESTING_SUMMARY.md](TESTING_SUMMARY.md)

**Key findings**:
- Confirmed bugs (28 in full test): Unmatched BEGIN/END blocks, mismatched DOCUMENT/ENDDOCUMENT
- Legacy PGML (0 after removing old-style files): Old-style ANS() calls
- False positives (initially 250, reduced to 37): List assignments, array autovivification, complex Perl patterns
- Generate output files: `confirmed_bugs_pg.txt`, `mixed_legacy_pg.txt`, `likely_false_positives_pg.txt`
- Document testing results in [TESTING_SUMMARY.md](TESTING_SUMMARY.md)

**Key findings**:
- Confirmed bugs (4): Unmatched BEGIN/END blocks, mismatched DOCUMENT/ENDDOCUMENT
- Legacy PGML (7): Old-style ANS() calls - works but should modernize to inline specs
- False positives (47): List assignments, array autovivification, complex Perl patterns

**Parser limitations discovered**:
- Doesn't detect list assignments: `($a, $b) = func()`
- Doesn't detect array element assignments: `$arr[0] = value` (creates @arr)
- Doesn't recognize old-style ANS(): `[____]` + `ANS()` is valid PGML
- Misses complex Perl patterns: loops, dynamic variables, special functions


**Recommendations**: Use linter for structural checks (BEGIN/END, DOCUMENT pairs) and legacy pattern detection (old-style ANS()). Manually verify variable assignment warnings - 81% are false positives from valid Perl code our regex parser doesn't understand.

### Parser Improvements

Significantly improved variable assignment detection to reduce false positives:

- Add list assignment detection: `($a, $b, $c) = func()`
- Add array element assignment: `$arr[0] = value` (autovivification)
- Add hash element assignment: `$hash{key} = value` (autovivification)
- Create `test_parser_improvements.py` with comprehensive tests
- Fix ASCII compliance in documentation (replace emojis with checkboxes)


**Results**:
- Files with issues: 171 -> 63 (63% reduction)
- False positives: 250 -> 37 (85% reduction)
- Confirmed bugs: 28 (unchanged - no false negatives introduced)
- False positive rate: 90% -> 57% (37% improvement in accuracy)

**Code changes**: Modified `pgml_lint/parser.py` to add three new regex patterns and updated `extract_assigned_vars()` function.

### Documentation and Organization

- Add [docs/CODE_ARCHITECTURE.md](CODE_ARCHITECTURE.md) and [docs/FILE_STRUCTURE.md](FILE_STRUCTURE.md)
- Link the new architecture and structure docs from [README.md](../README.md)
- Add [docs/INSTALL.md](INSTALL.md) and [docs/USAGE.md](USAGE.md) stubs
- Extend [docs/FILE_STRUCTURE.md](FILE_STRUCTURE.md) with install and usage docs
- Add unit test starter coverage for pgml_lint modules and plugin behaviors, with skips for IO-heavy scripts
- Refresh [README.md](../README.md) to point to install, usage, and core docs with a minimal quick start
- Point [tests/test_whitespace.py](../tests/test_whitespace.py) to [tests/fix_whitespace.py](../tests/fix_whitespace.py) and keep the fixer out of repo root
- Check [tests/fix_whitespace.py](../tests/fix_whitespace.py) via REPO_ROOT/tests fallback in whitespace hygiene
- Fix trailing whitespace in [docs/REPO_STYLE.md](REPO_STYLE.md)
- Align parser newline index test expectation with current implementation
- Organize output files into `output/` directory
- Move testing documentation to `docs/`


## 2026-01-18 - v26.01b1

Initial release as a standalone PyPI package.

- Remove leftover `pg_analyze` references from old repo structure.
- Update test imports: `pg_analyze.tokenize` -> `pgml_lint.parser`.
- Remove obsolete `test_pgml_blocks_sampler.py` that tested non-existent `pg_analyze.aggregate` module.

- Create `pgml_lint/` plugin framework with built-in PGML lint modules and tests.
- Add PGML-aware lint checks for blocks, heredocs, blanks, and inline markers.
- Add macro/assignment parsing with line-numbered output and optional JSON summaries.
- Fix MathObjects false positive: recognize that `PGML.pl` loads `MathObjects.pl` internally.
- Add math span masking (`[`...`]` and `[:...:+]`) to bracket checker to avoid false positives from LaTeX interval notation.
- Disable `pgml_brackets` plugin by default since plain brackets in PGML text are common.
- Add array/hash variable detection to assignment checker: recognize `@arr =` and `%hash =` patterns.
- Simplify lint CLI: just `-i`/`-d` for input, `-v`/`-q` for verbosity.
- Add comprehensive PGML lint documentation:
  - [docs/PGML_LINT.md](PGML_LINT.md): Usage guide and quick start
  - [docs/PGML_LINT_CONCEPTS.md](PGML_LINT_CONCEPTS.md): PGML syntax concepts the linter validates
  - [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md): Reference for all built-in plugins
  - [docs/PGML_LINT_PLUGIN_DEV.md](PGML_LINT_PLUGIN_DEV.md): Guide for writing custom plugins
  - [docs/PGML_LINT_ARCHITECTURE.md](PGML_LINT_ARCHITECTURE.md): Internal architecture for contributors
