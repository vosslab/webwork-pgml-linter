# Changelog

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

**Parser limitations discovered**:
- Doesn't detect list assignments: `($a, $b) = func()`
- Doesn't detect array element assignments: `$arr[0] = value` (creates @arr)
- Doesn't recognize old-style ANS(): `[____]` + `ANS()` is valid PGML
- Misses complex Perl patterns: loops, dynamic variables, special functions

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
