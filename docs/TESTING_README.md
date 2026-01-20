# PGML Linter Testing Results

## Quick Summary

Tested 2,000 random PGML files from the Open Problem Library training set and found:

- [x] **4 confirmed bugs** - Real errors to fix
- [~] **7 legacy PGML files** - Old-style ANS() calls that work but should modernize
- [ ] **47 false positives** - Valid code our simple parser doesn't understand

## Output Files

### confirmed_bugs_pg.txt (4 issues)
Real structural bugs that should be fixed:
- 1 unmatched `END_PGML` without `BEGIN_PGML`
- 3 mismatched `DOCUMENT()` / `ENDDOCUMENT()` counts

### mixed_legacy_pg.txt (7 issues)
Files using old-style answer processing (still valid, but consider modernizing):
```perl
# Old style (flagged):
BEGIN_PGML
Answer: [____]
END_PGML
ANS($answer->cmp());

# Modern style (recommended):
BEGIN_PGML
Answer: [____]{$answer}
END_PGML
```

### likely_false_positives_pg.txt (47 issues)
Valid Perl code flagged because our simple regex parser doesn't understand:

1. **List assignments** (~20 issues)
   ```perl
   ($min, $Q1, $median, $Q3, $max) = five_point_summary(@data);
   ```

2. **Array autovivification** (~12 issues)
   ```perl
   foreach my $i (0..5) {
       $arr[$i] = Real($value);  # Creates @arr automatically
   }
   ```

3. **Complex Perl patterns** (~15 issues)
   - Loop-based variable creation
   - Dynamic array construction
   - Special function returns

## Linter Accuracy

| Metric | Value | Notes |
|--------|-------|-------|
| Files tested | 2,000 | Random sample |
| Issues flagged | 58 | Total |
| True bugs | 4 | 7% of flagged |
| Legacy code | 7 | 12% of flagged |
| False positives | 47 | 81% of flagged |

## What Works Well

[x] Detects structural issues (unmatched blocks)
[x] Detects legacy patterns (old-style ANS)
[x] Fast and easy to run

## What Needs Work

[!] Too many false positives for variable checking (81%)
[!] Doesn't understand list assignments
[!] Doesn't understand array autovivification
[!] Needs more sophisticated Perl parsing

## How to Use

**Trust these warnings:**
- Unmatched BEGIN/END blocks -> Real bugs
- Mismatched DOCUMENT/ENDDOCUMENT -> Real bugs
- Missing answer specs (if no ANS() call) -> Real bugs
- Old-style ANS() usage -> Legacy code to modernize

**Manually verify these:**
- "PGML blank references $var without assignment" -> 81% false positive
- Check the file yourself - likely uses list assignment or loop

## Testing Scripts

- `test_random_pgml_subset.py` - Test linter on random file samples
- `categorize_lint_issues.py` - Initial categorization
- `recategorize_conservative.py` - Conservative validation with manual checks

See [TESTING_SUMMARY.md](TESTING_SUMMARY.md) for detailed analysis.
