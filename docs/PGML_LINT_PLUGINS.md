# PGML Lint Plugin Reference

This document describes each built-in plugin, what it checks, and example issues.

## Overview

| Plugin ID | Default | Description |
|-----------|---------|-------------|
| `block_markers` | Yes | BEGIN/END block pairing |
| `pgml_heredocs` | Yes | PGML heredoc terminators |
| `document_pairs` | Yes | DOCUMENT/ENDDOCUMENT pairing |
| `block_rules` | Yes | Custom block rule counts |
| `pgml_header_tags` | Yes | PG header tag quality |
| `pgml_include_pgproblem` | Yes | includePGproblem usage |
| `pgml_required_macros` | Yes | PGML requires PGML.pl |
| `pgml_loadmacros_integrity` | Yes | loadMacros syntax integrity |
| `macro_rules` | Yes | Macro requirement coverage |
| `pgml_seed_stability` | Yes | Seed stability checks |
| `pgml_seed_variation` | Yes | Seed variation detection |
| `pgml_function_signatures` | Yes | Function signature checks |
| `pgml_inline` | Yes | PGML inline markers [@ @] |
| `pgml_pgml_parse_hazards` | Yes | PGML parse hazard checks |
| `pgml_modes_in_inline` | Yes | MODES used inside inline eval |
| `pgml_modes_tex_payload` | Yes | MODES TeX payloads should be empty |
| `pgml_modes_html_plain_text` | Yes | MODES HTML payloads without tags |
| `pgml_inline_pgml_syntax` | Yes | PGML syntax inside inline code |
| `pgml_inline_braces` | Yes | PGML inline brace balance |
| `pgml_blanks` | Yes | PGML blank specs |
| `pgml_underscore_emphasis` | Yes | PGML underscore emphasis balance |
| `pgml_brackets` | No | PGML bracket balance |
| `pgml_blank_assignments` | Yes | Variable assignment checking |
| `pgml_line_length` | Yes | Extreme line length warnings |
| `pgml_blob_payloads` | Yes | Embedded blob payload hints |
| `pgml_label_dot` | Yes | Label dot list parsing trap |
| `pgml_ans_style` | Yes | PGML answer style consistency |
| `pgml_text_blocks` | Yes | Deprecated TEXT blocks |
| `pgml_html_in_text` | Yes | Raw HTML in PGML text |
| `pgml_nbsp` | Yes | Non-breaking space detection |
| `pgml_mojibake` | Yes | Mojibake/encoding glitches |
| `pgml_tex_color` | Yes | TeX color command warnings |
| `pgml_html_policy` | Yes | HTML policy checks |
| `pgml_html_forbidden_tags` | Yes | Forbidden HTML table tags in PGML |
| `pgml_html_div` | Yes | HTML div tags in PGML |
| `pgml_span_interpolation` | Yes | Span HTML interpolation checks |
| `pgml_html_var_passthrough` | Yes | HTML variables without passthrough |
| `pgml_style_string_quotes` | Yes | Unescaped quotes in PGML style strings |
| `pgml_tag_wrapper_tex` | Yes | PGML tag wrappers with TeX payloads |
| `pgml_ans_rule` | Yes | Legacy ans_rule() function |
| `pgml_br_variable` | Yes | Legacy $BR variable |
| `pgml_modes_html_escape` | Yes | MODES HTML escaped in interpolation |
| `pgml_old_answer_checkers` | Yes | Legacy answer checker functions |
| `pgml_solution_hint_macros` | Yes | Legacy SOLUTION/HINT macros |
| `pgml_pgml_wrapper_in_string` | Yes | PGML wrapper syntax in strings |

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

## pgml_loadmacros_integrity

**File:** `pgml_lint/plugins/pgml_loadmacros_integrity.py`

**Purpose:** Validate loadMacros() syntax for common compile errors.

**Checks:**
- Missing closing parenthesis.
- Missing trailing semicolon.
- Empty macro list.
- Missing commas between macro entries.

**Example Issues:**
```
file.pg:5: ERROR: loadMacros() missing closing parenthesis
file.pg:8: ERROR: loadMacros() missing trailing semicolon
file.pg:7: ERROR: loadMacros() entries appear to be missing a comma
```

## macro_rules

**File:** `pgml_lint/plugins/macro_rules.py`

**Purpose:** Checks that functions are used with their required macro files.

**Default Rules:**

| Function Pattern | Required Macro(s) |
|-----------------|-------------------|
| `Context()`, `Compute()`, `Formula()`, `Real()` | `MathObjects.pl` or `PGML.pl` |
| `RadioButtons()` | `parserRadioButtons.pl` or `parserMultipleChoice.pl` or `PGchoicemacros.pl` |
| `CheckboxList()` | `parserCheckboxList.pl` or `parserMultipleChoice.pl` or `PGchoicemacros.pl` |
| `PopUp()` | `parserPopUp.pl` or `parserMultipleChoice.pl` or `PGchoicemacros.pl` |
| `DropDown()` | `parserPopUp.pl` or `parserMultipleChoice.pl` or `PGchoicemacros.pl` |
| `MultiAnswer()` | `parserMultiAnswer.pl` |
| `OneOf()` | `parserOneOf.pl` |
| `NchooseK()` | `PGchoicemacros.pl` |
| `FormulaUpToConstant()` | `parserFormulaUpToConstant.pl` |
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

**Versioning:** Rules may include `min_pg_version` and `max_pg_version` to flag
features outside your target PG version. By default the linter targets PG 2.17.
To lint for PG 2.17 explicitly, pass `--pg-version 2.17` to
`tools/webwork_pgml_simple_lint.py` or supply the value in a custom integration.

**Configuration:** Via `--rules` JSON file with `macro_rules` array.

## pgml_seed_stability

**File:** `pgml_lint/plugins/pgml_seed_stability.py`

**Purpose:** Warn on non-seeded randomness or clock usage that can break seed stability.

**Checks:**
- `rand()` or `srand()` usage.
- Time-based calls (`time()`, `localtime()`, `gmtime()`).
- Explicit reseed helpers like `SRAND()`, `ProblemRandomize()`, or
  `PeriodicRerandomization()`.
  See [docs/RANDOMIZATION_METHODS.md](RANDOMIZATION_METHODS.md) for the inventory used
  to inform the pattern list.

**Example Issues:**
```
file.pg:23: WARNING: rand() may bypass PG seeding; use random() or list_random().
file.pg:45: WARNING: time() makes values depend on the clock; avoid for stable seeds.
```

## pgml_seed_variation

**File:** `pgml_lint/plugins/pgml_seed_variation.py`

**Purpose:** Warn when no seed-based randomization is detected.

**Checks:**
- Looks for common randomization or seed patterns (`random`, `list_random`, `shuffle`,
  `random_subset`, `PGrandom`, `rand`, `$problemSeed`).
  See [docs/RANDOMIZATION_METHODS.md](RANDOMIZATION_METHODS.md) for the inventory used
  to inform the pattern list.

**Example Issues:**
```
file.pg: WARNING: No seed-based randomization detected; answer may not vary with seed
```

## pgml_function_signatures

**File:** `pgml_lint/plugins/pgml_function_signatures.py`

**Purpose:** Validate common function signatures and empty argument lists.

**Checks:**
- Expected argument counts for common PG functions (random, NchooseK).
- Minimum argument counts for common constructors (Compute, Formula, DropDown).
- Known function name typos (Popup vs PopUp).

**Example Issues:**
```
file.pg:12: ERROR: random() called with 2 args; expected at least 3
file.pg:20: WARNING: DropDown() called with 1 args; expected at least 2
file.pg:30: ERROR: Function name 'Dropdown' looks wrong; use 'DropDown'
```

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

## pgml_pgml_parse_hazards

**File:** `pgml_lint/plugins/pgml_pgml_parse_hazards.py`

**Purpose:** Detect common PGML parse hazards that trigger renderer errors.

**Checks:**
- Unknown PGML block tokens like `[balance]`.
- Unbalanced parentheses inside `[@ @]` inline code blocks.
- PGML tag wrapper `[< ... >]` not closed before line break.

**Example Issues:**
```
file.pg:40: WARNING: Unknown PGML block token [balance] may cause parser errors
file.pg:45: WARNING: PGML inline code has unbalanced parentheses
file.pg:50: ERROR: PGML tag wrapper '[<' must be closed before line break
```

## pgml_modes_in_inline

**File:** `pgml_lint/plugins/pgml_modes_in_inline.py`

**Purpose:** Detect MODES() calls inside `[@ @]` eval blocks.

**Checks:**
- Warns when MODES() appears inside inline eval blocks.
- PG 2.17 exception: suppresses warnings when MODES uses `TeX => ''` and
  `HTML => '<div...>'` (or `<span>`, `<br>`, `<sup>`, `<sub>`) for layout.
- Warns when layout HTML is used but `TeX` is not empty in PG 2.17 mode.

**Example Issues:**
```
file.pg:20: WARNING: MODES() used inside [@ @] block; MODES returns 1 in eval context and will not emit HTML
```

## pgml_modes_tex_payload

**File:** `pgml_lint/plugins/pgml_modes_tex_payload.py`

**Purpose:** Warns when MODES() uses non-empty TeX payloads.

**Checks:**
- Flags any `TeX =>` entry that is not an empty string or empty `q{}`/`qq{}`.

**Example Issues:**
```
file.pg:42: WARNING: MODES() TeX payload is non-empty; use TeX => '' for PGML output
```

## pgml_modes_html_plain_text

**File:** `pgml_lint/plugins/pgml_modes_html_plain_text.py`

**Purpose:** Warns when MODES() HTML payloads contain no HTML tags.

**Checks:**
- Flags `MODES(HTML => '...')` when the HTML value is plain text.
- Suggests replacing the call with a plain string.

**Example Issues:**
```
file.pg:42: WARNING: MODES() HTML payload has no HTML tags; replace with plain string instead of MODES()
```

## pgml_inline_pgml_syntax

**File:** `pgml_lint/plugins/pgml_inline_pgml_syntax.py`

**Purpose:** Detects attempts to emit PGML structural syntax from inside `[@ ... @]*` blocks.

**Checks:**
- `[@ ... @]*` blocks containing PGML wrapper syntax like `[<` or `>]{`
- Nested `BEGIN_PGML` or `END_PGML` inside inline code
- PGML interpolation patterns like `[$answer]` inside inline string literals

**Example Issues:**
```
file.pg:42: ERROR: PGML tag wrapper token '[<' found inside [@ @] block
file.pg:44: ERROR: Nested BEGIN_PGML found inside [@ @] block
file.pg:46: ERROR: PGML interpolation [$answer_html] found inside [@ @] block; PGML parses once and will not re-parse strings
```

## pgml_inline_braces

**File:** `pgml_lint/plugins/pgml_inline_braces.py`

**Purpose:** Detects unbalanced `{` and `}` braces inside PGML inline Perl blocks.

**Checks:**
- `{` without matching `}` inside `[@ ... @]*`
- `}` without matching `{` inside `[@ ... @]*`

**Example Issues:**
```
file.pg:42: ERROR: PGML inline code has unclosed '{' brace
file.pg:44: ERROR: PGML inline code has unbalanced '}' brace
```

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

## pgml_underscore_emphasis

**File:** `pgml_lint/plugins/pgml_underscore_emphasis.py`

**Purpose:** Detects unbalanced underscore emphasis markers in PGML text.

**Checks:**
- `_` emphasis markers that are not closed before paragraph ends
- Skips inline code, answer blanks, and PGML math spans

**Example Issues:**
```
file.pg:30: WARNING: PGML underscore emphasis not closed before paragraph ends
```

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

## pgml_label_dot

**File:** `pgml_lint/plugins/pgml_label_dot.py`

**Purpose:** Warns when labels are built as `A.` which can trigger PGML list parsing.

**Checks:**
- Perl code patterns like `chr(65 + $i) . '. '`

**Example Issues:**
```
file.pg:18: WARNING: Label built as A. (chr(65 + $i) . '. ') can trigger PGML list parsing; use '*A.*' or 'A)' instead
```

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
- HTML structure tags: `<p>`, `<br>` (outside `[@ @]*` blocks)
- Math-related tags: `<sub>`, `<sup>`
- Other deprecated tags: `<font>`, `<center>`, `<a>`
- HTML entities: `&nbsp;`, `&lt;`, `&gt;`, `&copy;`, etc.
- MathJax suppression class: `class="tex2jax_ignore"`
- Span/style tags: `<span>`, `<style>`

**Why This Matters:**
PGML has its own markup language. Raw HTML in PGML text gets stripped or mangled during parsing, leading to unexpected output. Authors should use PGML markup instead.

**Example Issues:**
```
file.pg:25: WARNING: Raw HTML <strong> tag in PGML text will be stripped or mangled; use *bold* for bold text
file.pg:27: WARNING: Raw HTML <sub> tag in PGML text will be stripped or mangled; use LaTeX subscripts like [` x_2 `] for math
file.pg:30: WARNING: HTML entity '&nbsp;' in PGML text may be mangled; use Unicode characters or LaTeX instead
file.pg:34: WARNING: HTML class "tex2jax_ignore" found in PGML text; this suppresses MathJax and often indicates rendering problems
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
| `&nbsp;` | Use actual space or `~` in LaTeX |
| `&lt;` or `&gt;` | Use `<` or `>` directly, or in LaTeX mode |

**Table Tags:** See `pgml_html_forbidden_tags` for table-related HTML checks.

**Important Exception:**
HTML generated inside `[@ @]*` blocks is allowed and will not trigger warnings:
```perl
BEGIN_PGML
This is okay: [@ '<span class="highlight">text</span>' @]*
END_PGML
```
Note: Other plugins like `pgml_html_div` and `pgml_html_forbidden_tags` may still flag specific HTML tags inside inline code.

## pgml_html_div

**File:** `pgml_lint/plugins/pgml_html_div.py`

**Purpose:** Flags `<div>` tags that appear in PGML output, including inside inline code.

**Checks:**
- `<div>` or `</div>` tags anywhere in PGML blocks (PG 2.18+ only)
- Escaped div tags like `&lt;div ...&gt;`

**Example Issues:**
```
file.pg:25: ERROR: HTML <div> tag found in PGML content; avoid HTML divs because they often render incorrectly
file.pg:27: ERROR: Escaped HTML <div> tag found in PGML output; this indicates HTML is being escaped instead of rendered
```

**PG 2.17 Compatibility:**
Raw `<div>` tags are allowed when targeting PG 2.17; prefer HTML-only layout
via `MODES(TeX => '', HTML => '<div...>')` so TeX output stays empty.

## pgml_html_forbidden_tags

**File:** `pgml_lint/plugins/pgml_html_forbidden_tags.py`

**Purpose:** Flags table-related HTML tags inside PGML content, even when embedded in inline code.

**Checks:**
- `<table>`, `<tr>`, `<td>`, `<th>`
- `<thead>`, `<tbody>`, `<tfoot>`, `<colgroup>`, `<col>`

**Example Issues:**
```
file.pg:25: ERROR: HTML <table> tag found in PGML content; use DataTable() or LayoutTable() from niceTables.pl
```

## pgml_span_interpolation

**File:** `pgml_lint/plugins/pgml_span_interpolation.py`

**Purpose:** Warns when variables containing `<span>` HTML are never interpolated with `[$var]` in PGML.

**Checks:**
- Variables assigned strings with `<span ...>` that do not appear in PGML as `[$var]`

**Example Issues:**
```
file.pg:18: WARNING: Variable $answers_html contains <span> HTML but is not interpolated with [$answers_html] in PGML; HTML may be escaped
```

## pgml_style_string_quotes

**File:** `pgml_lint/plugins/pgml_style_string_quotes.py`

**Purpose:** Detects PGML style markup stored in single-quoted Perl strings that contains unescaped single quotes.

**Checks:**
- PGML style tags like `[<label>]{['span', style => 'color: #...;']}{['','']}` inside single-quoted strings
- Skips PGML blocks (BEGIN_PGML...END_PGML) where the markup is legal

**Example Issues:**
```
file.pg:34: ERROR: PGML style tag inside single-quoted string contains unescaped single quotes; escape as \' or use double quotes or q{...}
```

**Fixes:**
- Use double quotes around the Perl string
- Escape inner quotes with `\\'`
- Use `q{...}` or `qq{...}` with a safe delimiter

## pgml_tag_wrapper_tex

**File:** `pgml_lint/plugins/pgml_tag_wrapper_tex.py`

**Purpose:** Warns when PGML tag wrappers provide non-empty TeX payloads.

**Checks:**
- Tag wrappers like `[<div>]{[ 'div' ]}{[ '\\parbox{...}', '}' ]}`
- Flags non-empty TeX payloads that should usually be empty

**Example Issues:**
```
file.pg:42: WARNING: PGML tag wrapper has non-empty TeX payload; use an empty TeX payload unless needed
```

**Fixes:**
- Prefer an empty TeX payload: `[<div>]{[ 'div' ]}{ }`
- Use a TeX payload only when TeX rendering needs special output

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

## pgml_header_tags

**File:** `pgml_lint/plugins/pgml_header_tags.py`

**Purpose:** Checks PG header metadata for missing or placeholder values.

**Checks:**
- Missing DESCRIPTION/ENDDESCRIPTION or empty DESCRIPTION content
- Missing KEYWORDS or malformed KEYWORDS(...) syntax
- KEYWORDS count outside 3-10 entries or duplicate keyword entries
- Missing DBsubject/DBchapter/DBsection
- Placeholder DBsubject values (WeBWorK, ZZZ-Inserted Text)
- Placeholder DBchapter/DBsection text (taxonomy/refer-to hints)
- Smart quotes in header metadata

**Example Issues:**
```
file.pg:1: WARNING: Missing DESCRIPTION block in header
file.pg:4: WARNING: KEYWORDS tag is malformed; expected KEYWORDS('k1','k2',...)
file.pg:1: WARNING: DBsubject 'WeBWorK' is a placeholder or noisy value
```

## pgml_include_pgproblem

**File:** `pgml_lint/plugins/pgml_include_pgproblem.py`

**Purpose:** Warns when a file delegates content to `includePGproblem()`.

**Checks:**
- Any use of `includePGproblem()` (linter cannot verify target file)
- Files that appear to contain only includePGproblem and no local content

**Example Issues:**
```
file.pg:12: WARNING: includePGproblem() used; target file not verified by linter
file.pg:12: WARNING: includePGproblem() appears to be the only content in this file
```

## pgml_line_length

**File:** `pgml_lint/plugins/pgml_line_length.py`

**Purpose:** Warns on extreme line lengths that often hide blobs or break readability.

**Checks:**
- Lines longer than 200 characters
- Lines longer than 400 characters (extra warning if no whitespace)

**Example Issues:**
```
file.pg:40: WARNING: Line length 412 exceeds 400 characters
file.pg:40: WARNING: Long line without whitespace suggests embedded blob payload
```

## pgml_blob_payloads

**File:** `pgml_lint/plugins/pgml_blob_payloads.py`

**Purpose:** Flags embedded base64-like data blobs in PG files.

**Checks:**
- Base64-like strings over 800 characters
- ggbbase64 or base64 => markers

**Example Issues:**
```
file.pg:90: WARNING: Base64-like blob payload detected; consider removing embedded data
file.pg:95: WARNING: ggbbase64 payload marker detected; avoid embedded applet blobs
```

## pgml_nbsp

**File:** `pgml_lint/plugins/pgml_nbsp.py`

**Purpose:** Warns on Unicode non-breaking space characters that can cause layout surprises.

**Checks:**
- U+00A0 and U+202F non-breaking spaces

**Example Issues:**
```
file.pg:15: WARNING: Non-breaking space detected; replace with a normal space to avoid layout surprises
```

## pgml_mojibake

**File:** `pgml_lint/plugins/pgml_mojibake.py`

**Purpose:** Flags mojibake sequences that indicate encoding mixups.

**Checks:**
- Common UTF-8/Latin-1 glitch sequences like \\u00c3\\u00a9 or \\u00e2\\u0080
- Standalone mojibake markers like \\u00c2 and \\u00c3 (often show up as Â or Ã)
- Unicode replacement character (\\ufffd)

**Example Issues:**
```
file.pg:22: WARNING: Possible mojibake sequence '\\u00c3\\u00a9' detected; check for UTF-8/Latin-1 encoding mixups
```

## pgml_tex_color

**File:** `pgml_lint/plugins/pgml_tex_color.py`

**Purpose:** Warns on TeX color commands that do not render reliably in PGML output.

**Checks:**
- \\color{...} and \\textcolor{...} in PG content

**Example Issues:**
```
file.pg:30: WARNING: TeX color commands (\color, \textcolor) do not render reliably in PGML; use PGML tag wrappers or HTML spans instead
```

## pgml_html_policy

**File:** `pgml_lint/plugins/pgml_html_policy.py`

**Purpose:** Enforce HTML policy rules outside PGML safe pathways.

**Checks:**
- Disallowed tags like `<script>`, `<iframe>`, `<object>`, `<embed>`.
- Table tags outside PGML blocks (common in MODES HTML).
- Form/input tags that are likely sanitized.
- Escaped HTML tags (output shows HTML escaping).
- Inline `<style>` tags outside HEADER_TEXT blocks.
- `tex2jax_ignore` class usage that suppresses MathJax.
- SVG/Canvas/Video/Audio tags that are commonly sanitized.
- Disallowed tags used inside PGML tag wrappers.

**Example Issues:**
```
file.pg:10: ERROR: HTML <script> tag detected; avoid raw HTML that can be sanitized
file.pg:12: ERROR: HTML <table> tag detected; avoid raw HTML that can be sanitized
file.pg:20: WARNING: HTML <form> tag detected; avoid raw HTML that can be sanitized
file.pg:25: WARNING: Inline <style> tag found outside HEADER_TEXT; may be sanitized
file.pg:28: WARNING: HTML class "tex2jax_ignore" found; MathJax is suppressed and output may not render
```

## pgml_html_var_passthrough

**File:** `pgml_lint/plugins/pgml_html_var_passthrough.py`

**Purpose:** Warn when HTML stored in variables is output without raw passthrough.

**Checks:**
- Variables assigned HTML tags that are output as `[$var]` without a trailing `*`.

**Example Issues:**
```
file.pg:15: WARNING: Variable $label contains HTML but is output without raw passthrough; use [$label]* to avoid escaping
```

## pgml_pgml_wrapper_in_string

**File:** `pgml_lint/plugins/pgml_pgml_wrapper_in_string.py`

**Purpose:** Warn when PGML tag wrapper syntax appears inside Perl strings.

**Checks:**
- String literals containing `[<` or `]{[` patterns.

**Example Issues:**
```
file.pg:12: WARNING: PGML tag wrapper syntax found inside a Perl string; PGML parses once and will not re-parse strings
```

## Plugin Execution Order

Plugins run in registration order (as listed in `BUILTIN_PLUGINS`). Some plugins depend on data from earlier plugins:

1. `pgml_inline` runs first among PGML content plugins, stores `pgml_inline_spans`
2. `pgml_blanks` uses inline spans, stores `pgml_blank_vars` and `pgml_blank_spans`
3. `pgml_brackets` uses both inline and blank spans
4. `pgml_blank_assignments` uses `pgml_blank_vars`
5. `pgml_pgml_parse_hazards` uses `pgml_inline_spans` when present
6. `pgml_modes_in_inline` uses `pgml_inline_spans` when present

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
