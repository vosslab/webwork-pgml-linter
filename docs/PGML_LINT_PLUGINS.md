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
| `pgml_text_blocks` | Yes | Deprecated TEXT blocks |
| `pgml_html_in_text` | Yes | Raw HTML in PGML text |
| `pgml_ans_rule` | Yes | Legacy ans_rule() function |
| `pgml_br_variable` | Yes | Legacy $BR variable |
| `pgml_modes_html_escape` | Yes | MODES HTML escaped in interpolation |
| `pgml_old_answer_checkers` | Yes | Legacy answer checker functions |
| `pgml_solution_hint_macros` | Yes | Legacy SOLUTION/HINT macros |

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

## pgml_text_blocks

**File:** `pgml_lint/plugins/pgml_text_blocks.py`

**Purpose:** Flags deprecated BEGIN_TEXT/END_TEXT blocks as legacy PG syntax.

**Checks:**
- Presence of `BEGIN_TEXT` markers in the file

**Rationale:**
This linter enforces modern PGML standards for WebWork problems. `BEGIN_TEXT/END_TEXT` blocks are legacy PG syntax that should be migrated to `BEGIN_PGML/END_PGML` with PGML.pl. Modern PGML provides:
- Better LaTeX integration
- Cleaner inline answer syntax
- More consistent markup language
- Improved readability

**Example Issues:**
```
file.pg:15: WARNING: BEGIN_TEXT is deprecated legacy PG syntax; use BEGIN_PGML with PGML.pl for modern WebWork problems
```

**Migration Guide:**
Replace TEXT blocks with PGML blocks:

**Old (Legacy PG):**
```perl
BEGIN_TEXT
Compute \(2 + 2\).
$BR
Answer: \{ans_rule(10)\}
END_TEXT
```

**New (Modern PGML):**
```perl
BEGIN_PGML
Compute [` 2 + 2 `].

Answer: [_]{$answer}
END_PGML
```

## pgml_html_in_text

**File:** `pgml_lint/plugins/pgml_html_in_text.py`

**Purpose:** Detects raw HTML tags and entities in PGML text that will be stripped or mangled.

**Checks:**
- Problematic HTML formatting tags: `<strong>`, `<b>`, `<i>`, `<em>`, `<u>`
- HTML structure tags: `<p>`, `<br>`, `<div>` (outside `[@ @]*` blocks)
- Math-related tags: `<sub>`, `<sup>`
- Table tags: `<table>`, `<tr>`, `<td>`, `<th>`
- Other deprecated tags: `<font>`, `<center>`, `<a>`
- HTML entities: `&nbsp;`, `&lt;`, `&gt;`, `&copy;`, etc.

**Why This Matters:**
PGML has its own markup language. Raw HTML in PGML text gets stripped or mangled during parsing, leading to unexpected output. Authors should use PGML markup instead.

**Example Issues:**
```
file.pg:25: WARNING: Raw HTML <strong> tag in PGML text will be stripped or mangled; use *bold* for bold text
file.pg:27: WARNING: Raw HTML <sub> tag in PGML text will be stripped or mangled; use LaTeX subscripts like [` x_2 `] for math
file.pg:30: WARNING: HTML entity '&nbsp;' in PGML text may be mangled; use Unicode characters or LaTeX instead
```

**HTML -> PGML Migration Guide:**

| HTML | PGML Alternative |
|------|------------------|
| `<strong>text</strong>` or `<b>text</b>` | `*text*` (bold) |
| `<em>text</em>` or `<i>text</i>` | `_text_` (italic) |
| `<sub>2</sub>` | `` [` H_2O `] `` (LaTeX subscript) |
| `<sup>2</sup>` | `` [` x^2 `] `` (LaTeX superscript) |
| `<br>` or `<br/>` | Blank line in PGML |
| `<p>text</p>` | Blank lines for paragraphs |
| `<table>` | `DataTable()` or `LayoutTable()` from niceTables.pl |
| `&nbsp;` | Use actual space or `~` in LaTeX |
| `&lt;` or `&gt;` | Use `<` or `>` directly, or in LaTeX mode |

**Important Exception:**
HTML generated inside `[@ @]*` blocks is allowed and will not trigger warnings:
```perl
BEGIN_PGML
This is okay: [@ '<span class="highlight">text</span>' @]*
END_PGML
```

## pgml_ans_rule

**File:** `pgml_lint/plugins/pgml_ans_rule.py`

**Purpose:** Detects legacy ans_rule() function calls that should be replaced with PGML inline answer blanks.

**Checks:**
- `ans_rule()` function calls anywhere in the code

**Rationale:**
`ans_rule()` is old-style PG syntax typically used with BEGIN_TEXT blocks. Modern PGML provides inline answer syntax that's cleaner and more readable.

**Example Issues:**
```
file.pg:15: WARNING: ans_rule() is deprecated legacy PG syntax; use PGML inline answer blanks like [_]{$answer} instead
```

**Migration Guide:**

**Old (Legacy PG):**
```perl
BEGIN_TEXT
Enter your answer: \{ans_rule(20)\}
END_TEXT

ANS($answer->cmp());
```

**New (Modern PGML):**
```perl
BEGIN_PGML
Enter your answer: [_____]{$answer}
END_PGML
```

## pgml_br_variable

**File:** `pgml_lint/plugins/pgml_br_variable.py`

**Purpose:** Detects legacy $BR variable usage for line breaks.

**Checks:**
- `$BR` variable references anywhere in the code

**Rationale:**
`$BR` is old-style PG syntax for inserting line breaks. Modern PGML uses blank lines for paragraph breaks, making the markup more readable.

**Example Issues:**
```
file.pg:20: WARNING: $BR is deprecated legacy PG syntax; use blank lines in PGML for paragraph breaks
```

**Migration Guide:**

**Old (Legacy PG):**
```perl
BEGIN_TEXT
Line one
$BR
Line two
$BR
Line three
END_TEXT
```

**New (Modern PGML):**
```perl
BEGIN_PGML
Line one

Line two

Line three
END_PGML
```

**Note:** For spacing within a paragraph, just use regular line breaks in the source. PGML treats single line breaks as spaces, and double line breaks (blank lines) as paragraph breaks.

## pgml_modes_html_escape

**File:** `pgml_lint/plugins/pgml_modes_html_escape.py`

**Purpose:** Detects when HTML from MODES() is incorrectly used with `[$var]` interpolation, causing it to be escaped.

**The Problem:**
PGML automatically escapes any HTML that arrives via `[$var]` interpolation, even if the string was produced by `MODES(HTML => '<span ...>', ...)`. This means your carefully formatted HTML will be displayed as literal text like `&lt;span ...&gt;` instead of being rendered.

**Checks:**
- Variables assigned from `MODES()` with HTML content
- Uses of those variables in `[$var]` interpolation within PGML blocks
- Does NOT warn about `[@ $var @]*` (which correctly renders HTML)

**Example Issues:**
```
file.pg:25: WARNING: Variable $html contains HTML from MODES() but is used in [$var] interpolation which escapes HTML; use [@ $html @]* instead to render HTML
```

**The Bug Explained:**

**Incorrect (HTML gets escaped):**
```perl
$formatted = MODES(
	TeX => '\\textbf{bold}',
	HTML => '<strong>bold</strong>'
);

BEGIN_PGML
This displays: &lt;strong&gt;bold&lt;/strong&gt;
[$formatted]
END_PGML
```

**Correct (HTML renders properly):**
```perl
$formatted = MODES(
	TeX => '\\textbf{bold}',
	HTML => '<strong>bold</strong>'
);

BEGIN_PGML
This displays: **bold** (rendered)
[@ $formatted @]*
END_PGML
```

**Why This Matters:**
This is a subtle bug that's easy to miss during development. The problem won't show up until you view the rendered page and notice escaped HTML tags appearing as literal text. This plugin catches it at lint time.

**Technical Details:**
- `[$var]` - PGML interpolation that escapes HTML for safety
- `[@ $var @]*` - Inline code block that outputs raw HTML/TeX
- MODES() often produces HTML strings, which need the raw output syntax

## pgml_old_answer_checkers

**File:** `pgml_lint/plugins/pgml_old_answer_checkers.py`

**Purpose:** Detects legacy answer checker functions that should be replaced with MathObjects.

**Checks:**
- `num_cmp()` - Old numeric answer checker
- `str_cmp()` - Old string answer checker
- `fun_cmp()` - Old function answer checker
- `std_num_cmp()`, `std_str_cmp()`, `std_fun_cmp()` - Standard variants
- `strict_num_cmp()`, `strict_str_cmp()` - Strict variants

**Rationale:**
Old answer checker functions are deprecated in favor of MathObjects, which provide better type safety, more consistent behavior, and cleaner syntax.

**Example Issues:**
```
file.pg:15: WARNING: num_cmp() is deprecated legacy PG syntax; use MathObjects with ->cmp() method instead (e.g., $answer->cmp())
file.pg:20: WARNING: str_cmp() is deprecated legacy PG syntax; use MathObjects with ->cmp() method instead (e.g., $answer->cmp())
```

**Migration Guide:**

**Old (Legacy PG):**
```perl
$answer = 42;
ANS(num_cmp($answer));

$string = "correct";
ANS(str_cmp($string));

$formula = "x^2 + 1";
ANS(fun_cmp($formula, var => 'x'));
```

**New (Modern MathObjects):**
```perl
$answer = Compute("42");
ANS($answer->cmp());

$string = String("correct");
ANS($string->cmp());

$formula = Formula("x^2 + 1");
ANS($formula->cmp());
```

**In PGML (even simpler):**
```perl
$answer = Compute("42");

BEGIN_PGML
Answer: [_]{$answer}
END_PGML
```

## pgml_solution_hint_macros

**File:** `pgml_lint/plugins/pgml_solution_hint_macros.py`

**Purpose:** Detects legacy SOLUTION() and HINT() macros that should use PGML blocks.

**Checks:**
- `SOLUTION()` macro calls (case-insensitive)
- `HINT()` macro calls (case-insensitive)

**Rationale:**
Old-style `SOLUTION(EV3(<<'END'))` and `HINT(EV3(<<'END'))` macros are deprecated. Modern PGML provides cleaner block syntax for solutions and hints.

**Example Issues:**
```
file.pg:25: WARNING: SOLUTION() macro is deprecated legacy PG syntax; use BEGIN_PGML_SOLUTION...END_PGML_SOLUTION blocks instead
file.pg:30: WARNING: HINT() macro is deprecated legacy PG syntax; use BEGIN_PGML_HINT...END_PGML_HINT blocks instead
```

**Migration Guide:**

**Old (Legacy PG):**
```perl
SOLUTION(EV3(<<'END_SOLUTION'));
To solve this problem:
1. First step
2. Second step
The answer is $answer.
END_SOLUTION

HINT(EV3(<<'END_HINT'));
Remember to consider all cases.
END_HINT
```

**New (Modern PGML):**
```perl
BEGIN_PGML_SOLUTION
To solve this problem:
1. First step
2. Second step

The answer is [$answer].
END_PGML_SOLUTION

BEGIN_PGML_HINT
Remember to consider all cases.
END_PGML_HINT
```

**Benefits of PGML blocks:**
- Cleaner syntax (no EV3, no heredoc terminators)
- PGML markup support (lists, math, formatting)
- Consistent with modern PGML style
- Easier to read and maintain

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
