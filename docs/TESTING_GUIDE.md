# Testing Guide for PGML Linter Results

## Overview

The linter found **171 files with issues** in 9,335 PGML files (1.8%):
- **28 confirmed bugs** in 27 files
- **250 false positives** in 144 files

## Files for Manual Testing

### Confirmed Bugs

Test these in WeBWorK renderer - they should **fail or have errors**:

#### 1. `bugs_document_pairs.txt` (15 files)
**Issue**: Mismatched DOCUMENT() / ENDDOCUMENT() counts
- 12 CCCS files with 1 DOCUMENT, 2 ENDDOCUMENT
- 3 other files with mismatches

**Test one**: `problems/Contrib/CCCS/CollegeAlgebra/6.2/CCD_CCCS_Openstax_AlgTrig_AT-1-001-AS_6_2_11.pg`

#### 2. `bugs_block_markers.txt` (11 files)
**Issue**: Unmatched END_PGML without matching BEGIN
- All 11 files are in `Contrib/CCCS/CalculusTwo/07.4/`
- Pattern: Commented out `#BEGIN_PGML_SOLUTION` but left `END_PGML` uncommented

**Test one**: `problems/Contrib/CCCS/CalculusTwo/07.4/CCD_CCCS_Openstax_Calc2_C1-2016-002_7_4_190.pg` (line 110)

#### 3. `bugs_pgml_blanks.txt` (1 file, 2 issues)
**Issue**: PGML blanks missing answer specs
- File: `problems/Contrib/CCCS/CalculusOne/03.6/CCD_CCCS_Openstax_Calc1_C1-2016-002_3_6_224.pg`
- Lines 56 and 58 have `[____]` without `{$answer}` and no ANS() call

### False Positives

Test these in WeBWorK renderer - they should **render correctly**:

#### `false_positives_common_vars.txt`

Shows the top 20 most-flagged variables with example files.

**Common patterns**:
- `$ans` (26 times) - Often typo for `$answer`, but check each
- `$ansInt` (14 times) - Interval answers, likely list assignment
- `$popup` (9 times) - Popup menus, check for dynamic creation
- `$median`, `$Q1`, `$Q3`, `$min`, `$max` - Statistics from `five_point_summary()`
- `$sum`, `$last`, `$pair` - Array elements from loops

**Test a few from each variable** to confirm they work despite the warning.

## Testing Procedure

### For Confirmed Bugs:

1. Pick a file from one of the `bugs_*.txt` files
2. Load it in WeBWorK renderer
3. **Expected**: File should fail to render or have errors
4. **If it renders fine**: It's a false positive - let me know!

### For False Positives:

1. Pick a file from `false_positives_common_vars.txt`
2. Load it in WeBWorK renderer
3. **Expected**: File should render correctly
4. **If it fails**: It's actually a bug - let me know!

## Quick Test Commands

Sample one file from each bug type:
```bash
# Document pairs issue
head -12 bugs_document_pairs.txt | tail -1

# Block markers issue
head -12 bugs_block_markers.txt | tail -1

# Blank spec issue
head -12 bugs_pgml_blanks.txt | tail -1
```

Sample false positives for $ans:
```bash
grep "^\$ans:" -A 4 false_positives_common_vars.txt
```

## Bug Type Breakdown

| Bug Type | Count | Files | Pattern |
|----------|-------|-------|---------|
| document_pairs | 15 | 15 | DOCUMENT/ENDDOCUMENT mismatch |
| block_markers | 11 | 11 | Uncommented END_PGML |
| pgml_blanks | 2 | 1 | Missing answer spec |
| **Total** | **28** | **27** | |

## Repository Breakdown

Where the bugs are:
- Contrib/CCCS: 21 bugs (75%)
- Contrib/RRCC: 4 bugs
- Contrib/PCC: 1 bug
- OpenProblemLibrary: 2 bugs

**Most bugs are in CCCS contributions** - likely systematic issues in those problem sets.

## Validation Results

From testing 2,000 random files:
- [x] Structural issues (block_markers, document_pairs): **100% accurate**
- [!] Variable assignments (pgml_blank_assignments): **81% false positive rate**

**Recommendation**: Trust structural bug warnings, but manually verify variable warnings.
