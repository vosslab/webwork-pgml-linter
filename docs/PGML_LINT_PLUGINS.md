# PGML Lint Plugin Reference

This document describes each built-in plugin, what it checks, and example issues.

## Overview

| Plugin ID | Default | Description |
|-----------|---------|-------------|
| `block_markers` | Yes | BEGIN/END block pairing |
| `pgml_heredocs` | Yes | PGML heredoc terminators |
| `document_pairs` | Yes | DOCUMENT/ENDDOCUMENT pairing |
| `block_rules` | Yes | Custom block rule counts |
| `pgml_required_macros` | Yes | PGML requires PGML.pl |
| `macro_rules` | Yes | Macro requirement coverage |
| `pgml_inline` | Yes | PGML inline markers [@ @] |
| `pgml_blanks` | Yes | PGML blank specs |
| `pgml_brackets` | No | PGML bracket balance |
| `pgml_blank_assignments` | Yes | Variable assignment checking |
| `pgml_ans_style` | Yes | PGML answer style consistency |

## block_markers

**File:** `pgml_lint/plugins/block_markers.py`

**Purpose:** Validates that BEGIN/END block markers are properly paired.

**Checks:**
- Unmatched `BEGIN_*` without corresponding `END_*`
- Unmatched `END_*` without corresponding `BEGIN_*`
- Mismatched pairs (e.g., `BEGIN_PGML` closed by `END_TEXT`)
- Nested PGML blocks (e.g., `BEGIN_PGML_HINT` inside `BEGIN_PGML`)

**Supported Markers:**
- `BEGIN_PGML` / `END_PGML`
- `BEGIN_PGML_SOLUTION` / `END_PGML_SOLUTION`
- `BEGIN_PGML_HINT` / `END_PGML_HINT`
- `BEGIN_TEXT` / `END_TEXT`
- `BEGIN_SOLUTION` / `END_SOLUTION`
- `BEGIN_HINT` / `END_HINT`

**Example Issues:**
```
file.pg:42: ERROR: END_PGML without matching BEGIN
file.pg:10: ERROR: BEGIN_PGML without matching END
file.pg:25: WARNING: BEGIN_PGML_HINT appears inside another PGML block
```

## pgml_heredocs

**File:** `pgml_lint/plugins/pgml_heredocs.py`

**Purpose:** Detects unterminated PGML heredoc blocks.

**Checks:**
- PGML heredocs (identified by `PGML` in terminator or `PGML::` in line) that are never closed

**Heredoc Patterns Detected:**
- `PGML::Format(<<END_PGML)`
- `<<END_PGML` where terminator contains "PGML"

**Example Issues:**
```
file.pg:15: ERROR: PGML heredoc terminator 'END_PGML' not found
file.pg:30: ERROR: PGML heredoc terminator 'END_PGML_HINT' not found
```

## document_pairs

**File:** `pgml_lint/plugins/document_pairs.py`

**Purpose:** Validates `DOCUMENT()` and `ENDDOCUMENT()` pairing.

**Checks:**
- `DOCUMENT()` present without `ENDDOCUMENT()`
- `ENDDOCUMENT()` present without `DOCUMENT()`
- Count mismatch between `DOCUMENT()` and `ENDDOCUMENT()`
- `ENDDOCUMENT()` appearing before `DOCUMENT()`

**Example Issues:**
```
file.pg:1: WARNING: DOCUMENT() present without ENDDOCUMENT()
file.pg: ERROR: DOCUMENT() count does not match ENDDOCUMENT() (start=1, end=2)
file.pg:5: ERROR: ENDDOCUMENT() appears before DOCUMENT()
```

## block_rules

**File:** `pgml_lint/plugins/block_rules.py`

**Purpose:** Applies custom count-based block rules from the rules file.

**Checks:**
- Start/end pattern counts match for custom block rules
- Excludes DOCUMENT/ENDDOCUMENT (handled by `document_pairs`)
- Excludes BEGIN_/END_ markers (handled by `block_markers`)

**Configuration:** Via `--rules` JSON file with `block_rules` array.

## pgml_required_macros

**File:** `pgml_lint/plugins/pgml_required_macros.py`

**Purpose:** Warns when PGML syntax is used without loading `PGML.pl`.

**Checks:**
- `BEGIN_PGML` or `PGML::` present but `pgml.pl` not in `loadMacros()`

**Example Issues:**
```
file.pg: WARNING: PGML used without required macros: pgml.pl
```

## macro_rules

**File:** `pgml_lint/plugins/macro_rules.py`

**Purpose:** Checks that functions are used with their required macro files.

**Default Rules:**

| Function Pattern | Required Macro(s) |
|-----------------|-------------------|
| `Context()`, `Compute()`, `Formula()`, `Real()` | `MathObjects.pl` or `PGML.pl` |
| `RadioButtons()` | `parserRadioButtons.pl` or `PGchoicemacros.pl` |
| `CheckboxList()` | `parserCheckboxList.pl` or `PGchoicemacros.pl` |
| `PopUp()` | `parserPopUp.pl` or `PGchoicemacros.pl` |
| `DataTable()` | `niceTables.pl` |
| `LayoutTable()` | `niceTables.pl` |
| `NumberWithUnits()` | `parserNumberWithUnits.pl` or `contextUnits.pl` |
| `Context('Fraction')` | `contextFraction.pl` |
| `DraggableSubsets()` | `draggableSubsets.pl` |

**Example Issues:**
```
file.pg: WARNING: MathObjects functions used without required macros: mathobjects.pl
file.pg: WARNING: DataTable used without required macros: nicetables.pl
```

**Configuration:** Via `--rules` JSON file with `macro_rules` array.

## pgml_inline

**File:** `pgml_lint/plugins/pgml_inline.py`

**Purpose:** Checks PGML inline code markers are properly paired.

**Checks:**
- `[@` without matching `@]`
- `@]` without matching `[@`

**Example Issues:**
```
file.pg:45: WARNING: PGML inline open [@ without matching @]
file.pg:50: WARNING: PGML inline close @] without matching [@
```

**Side Effects:** Stores `pgml_inline_spans` in context for downstream plugins.

## pgml_blanks

**File:** `pgml_lint/plugins/pgml_blanks.py`

**Purpose:** Validates PGML answer blank syntax.

**Checks:**
- Blanks missing answer spec: `[_]` without `{$answer}`
- Empty answer specs: `[_]{}`
- Unbalanced braces in answer spec
- Both payload and star specs: `[_]{$a}*{$b}`

**Blank Patterns:**
- `[_]{$answer}` - simple blank
- `[___]{$answer}` - wider blank
- `[____]*{$answer}` - star spec (grading modifier)

**Example Issues:**
```
file.pg:30: WARNING: PGML blank missing answer spec
file.pg:35: ERROR: PGML blank spec has unbalanced braces
file.pg:40: WARNING: PGML blank spec is empty
```

**Side Effects:** Stores `pgml_blank_vars` and `pgml_blank_spans` in context.

## pgml_brackets

**File:** `pgml_lint/plugins/pgml_brackets.py`

**Default:** Disabled (enable with `--enable pgml_brackets`)

**Purpose:** Checks for unbalanced brackets in PGML content.

**Checks:**
- `[` without matching `]`
- `]` without matching `[`

**Exclusions:** Ignores brackets inside:
- Inline code spans (`[@ @]`)
- Answer blanks (`[_]`)
- Math delimiters (`` [`...`] `` and `[:...:+]`)

**Why Disabled:** Plain brackets are common in PGML text, especially in:
- Interval notation: `(5,10]`
- Documentation examples
- Mathematical expressions in prose

**Example Issues:**
```
file.pg:55: WARNING: PGML bracket open [ without matching ]
file.pg:60: WARNING: PGML bracket close ] without matching [
```

## pgml_blank_assignments

**File:** `pgml_lint/plugins/pgml_blank_assignments.py`

**Purpose:** Warns when PGML blanks reference variables not assigned in the file.

**Checks:**
- Variables in `{$var}` specs that don't appear in assignments

**Assignment Patterns Recognized:**
- Scalar: `$var =`, `my $var`, `our $var`
- Array: `@arr =`, `my @arr`, `our @arr`
- Hash: `%hash =`, `my %hash`, `our %hash`

This allows detecting both direct variables and array/hash element access (e.g., `$arr[0]` when `@arr` is assigned).

**Example Issues:**
```
file.pg: WARNING: PGML blank references $answer without assignment in file
file.pg: WARNING: PGML blank references $popup without assignment in file
```

**Limitations:**
- Does not recognize all Perl assignment patterns (e.g., `my ($a, $b) = @_`)
- Does not track scope (may miss local variables in subroutines)
- May false-positive on variables defined via other means (method calls, etc.)

## pgml_ans_style

**File:** `pgml_lint/plugins/pgml_ans_style.py`

**Purpose:** Warns when ANS() calls appear after END_PGML blocks (mixing styles).

**Checks:**
- `ANS(...)` function calls appearing after `END_PGML` but before `ENDDOCUMENT()`

**Style Rationale:**
- Pure PGML style uses inline answer specs: `[_]{$answer}`
- Old PG style uses `ANS($answer->cmp())` after TEXT/PGML blocks
- Mixing these styles is inconsistent and can confuse readers

**Example Issues:**
```
file.pg:42: WARNING: ANS() call after END_PGML block (mixed style). Pure PGML uses inline answer specs: [_]{$answer} instead of ANS($answer->cmp())
```

**Good (Pure PGML Style):**
```perl
BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML
```

**Bad (Mixed Style):**
```perl
BEGIN_PGML
What is 6 times 7?

[_______]
END_PGML

ANS($answer->cmp());
```

**Note:** For RadioButtons and similar objects, use `[_]{$rb}` instead of displaying with `[@ $rb->buttons() @]*` and then calling `ANS($rb->cmp())`.

## Plugin Execution Order

Plugins run in registration order (as listed in `BUILTIN_PLUGINS`). Some plugins depend on data from earlier plugins:

1. `pgml_inline` runs first among PGML content plugins, stores `pgml_inline_spans`
2. `pgml_blanks` uses inline spans, stores `pgml_blank_vars` and `pgml_blank_spans`
3. `pgml_brackets` uses both inline and blank spans
4. `pgml_blank_assignments` uses `pgml_blank_vars`

## Disabling Noisy Plugins

If a plugin produces too many warnings for your codebase:

```bash
# Disable variable assignment checking
python3 tools/webwork_pgml_simple_lint.py --disable pgml_blank_assignments -d problems/

# Disable multiple plugins
python3 tools/webwork_pgml_simple_lint.py --disable pgml_blank_assignments,macro_rules -d problems/
```

## Enabling Optional Plugins

```bash
# Enable bracket checking
python3 tools/webwork_pgml_simple_lint.py --enable pgml_brackets -d problems/
```
