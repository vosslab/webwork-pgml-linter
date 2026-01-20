# Testing Documentation

This directory contains comprehensive testing documentation for the PGML linter.

## Quick Links

### Testing Results
- **[TESTING_README.md](TESTING_README.md)** - Quick overview of testing results
- **[TESTING_SUMMARY.md](TESTING_SUMMARY.md)** - Detailed testing analysis and findings
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Manual testing instructions

### Parser Improvements
- **[PARSER_IMPROVEMENTS_COMPLETE.md](PARSER_IMPROVEMENTS_COMPLETE.md)** - Complete parser improvement summary
- **[IMPROVEMENT_SUMMARY.md](IMPROVEMENT_SUMMARY.md)** - Before/after comparison

### General Documentation
- **[CHANGELOG.md](CHANGELOG.md)** - Complete change history

## Testing Summary

From testing 9,335 PGML files:

**Before Parser Improvements:**
- Files with issues: 171
- False positives: 250 (90% false positive rate)
- Confirmed bugs: 28

**After Parser Improvements:**
- Files with issues: 63 (63% reduction)
- False positives: 37 (85% reduction)
- Confirmed bugs: 28 (no false negatives!)
- False positive rate: 57% (37% improvement)

## Key Improvements

Added detection for:
1. List assignments: `($a, $b) = func()`
2. Array autovivification: `$arr[0] = value`
3. Hash autovivification: `$hash{key} = value`

## Testing Files (Repository Root)

The following test scripts and output files are in the repository root:

### Scripts
- `test_random_pgml_subset.py` - Test linter on random file samples
- `lint_and_categorize_all.py` - Lint all files and auto-categorize
- `categorize_lint_issues.py` - Categorize issues into buckets
- `recategorize_conservative.py` - Conservative validation
- `test_parser_improvements.py` - Test parser enhancements
- `analyze_results.py` - Detailed analysis of results
- `RUN_FULL_TEST.sh` - One-command full test

### Output Files
- `confirmed_bugs_pg.txt` - 28 confirmed bugs to fix
- `mixed_legacy_pg.txt` - Legacy ANS() patterns (if any)
- `likely_false_positives_pg.txt` - 37 false positives
- `bugs_document_pairs.txt` - DOCUMENT/ENDDOCUMENT mismatches
- `bugs_block_markers.txt` - Unmatched BEGIN/END blocks
- `bugs_pgml_blanks.txt` - Missing answer specs
- `false_positives_common_vars.txt` - Common false positive variables

## For Developers

If you want to:
- **Run the full test**: `./RUN_FULL_TEST.sh`
- **Test parser improvements**: `python3.12 test_parser_improvements.py`
- **Analyze results**: `python3.12 analyze_results.py`
- **Understand what was improved**: Read [PARSER_IMPROVEMENTS_COMPLETE.md](PARSER_IMPROVEMENTS_COMPLETE.md)

## For Users

If you want to:
- **Understand test results**: Read [TESTING_README.md](TESTING_README.md)
- **Manually validate bugs**: Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
- **See detailed analysis**: Read [TESTING_SUMMARY.md](TESTING_SUMMARY.md)
