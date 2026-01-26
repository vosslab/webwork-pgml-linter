# PGML lint plugin ideas

This document lists possible offline lint plugins for PGML and PG code, including
what already exists and what could be added. It is a planning reference for
future lint coverage and tests.

See [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md) for current plugin behavior
and [docs/PGML_LINT.md](PGML_LINT.md) for the user facing overview.

## Scope and constraints

- Offline only. No calls to the live renderer API.
- Static analysis on `.pg` source text.
- Prefer low false positive rules with clear messaging.
- Support line numbers when possible.
- Keep ASCII and ISO-8859-1 only.

## Current plugin inventory (implemented)

This is the current built-in set. The short summary here is for quick scanning.
Details and examples live in [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md).

| Plugin ID | Status | Summary |
| --- | --- | --- |
| `block_markers` | existing | BEGIN/END block pairing |
| `pgml_heredocs` | existing | Unterminated PGML heredocs |
| `document_pairs` | existing | DOCUMENT/ENDDOCUMENT pairing |
| `block_rules` | existing | Custom block count rules |
| `pgml_header_tags` | existing | Header metadata quality |
| `pgml_include_pgproblem` | existing | includePGproblem usage |
| `pgml_required_macros` | existing | PGML requires PGML.pl |
| `macro_rules` | existing | Function macro requirements |
| `pgml_inline` | existing | [@ @] marker pairing |
| `pgml_inline_pgml_syntax` | existing | PGML syntax inside inline code |
| `pgml_inline_braces` | existing | Inline brace balance |
| `pgml_blanks` | existing | PGML blank specs |
| `pgml_underscore_emphasis` | existing | Underscore emphasis balance |
| `pgml_brackets` | existing | Bracket balance (optional) |
| `pgml_blank_assignments` | existing | Undefined blank variables |
| `pgml_line_length` | existing | Extreme line lengths |
| `pgml_blob_payloads` | existing | Embedded blob markers |
| `pgml_label_dot` | existing | A. label parsing trap |
| `pgml_ans_style` | existing | Mixed PGML and ANS() styles |
| `pgml_text_blocks` | existing | Deprecated TEXT blocks |
| `pgml_html_in_text` | existing | Raw HTML in PGML text |
| `pgml_html_forbidden_tags` | existing | Forbidden table tags |
| `pgml_html_div` | existing | div tags in PGML |
| `pgml_span_interpolation` | existing | Span HTML interpolation |
| `pgml_style_string_quotes` | existing | Unescaped quotes in style strings |
| `pgml_ans_rule` | existing | Legacy ans_rule() |
| `pgml_br_variable` | existing | Legacy $BR |
| `pgml_modes_html_escape` | existing | MODES HTML escaping |
| `pgml_old_answer_checkers` | existing | Legacy answer checkers |
| `pgml_solution_hint_macros` | existing | Legacy SOLUTION/HINT macros |
| `pgml_nbsp` | existing | Non-breaking spaces |
| `pgml_mojibake` | existing | Encoding glitches |
| `pgml_tex_color` | existing | TeX color commands |

## Proposed plugin ideas

These are grouped as bigger picture plugins. Each plugin can bundle multiple
related checks, and each check should default to WARNING or ERROR. Avoid INFO
plugins unless there is a strong reason.

### Header and metadata quality

**`pgml_header_quality` (WARNING)**
- Date format enforcement: `## Date('YYYY-MM-DD')`.
- Required metadata presence (DESCRIPTION, KEYWORDS, DBsubject).
- Duplicate or conflicting tags (repeat DBsubject with different values).
- Smart quotes or encoding hazards in the header block.

### Function and macro correctness

**`pgml_function_signatures` (ERROR/WARNING)**
- Function existence and expected argument counts.
- Expected argument shapes (list vs scalar, string vs number).
- Empty argument lists in function calls (big picture check that covers
  `pgml_random_choice_empty` and similar).
- Data driven rules file that maps function -> expected args and messages.

**`pgml_loadmacros_integrity` (ERROR/WARNING)**
- Syntax errors in `loadMacros(...)` (missing commas, parens, semicolon).
- Smart quotes or mismatched quote styles in macro lists.
- Wrong case macro names (`PGML.pl` vs `pgml.pl`).
- Redundant or duplicate macro entries.

**`pgml_macro_coverage_extended` (WARNING)**
- Extend `macro_rules` with a wider function set (parser widgets, nicetables,
  context units, draggable widgets).
- One plugin for macro presence based on function usage.

### PGML parsing hazards

**`pgml_pgml_parse_hazards` (ERROR/WARNING)**
- Unbalanced emphasis markers (`*` and `_`) per paragraph.
- Nested or unclosed `[@ @]` inline blocks.
- Unbalanced braces or parens inside `[@ @]`.
- PGML tag wrapper syntax constructed inside Perl strings.
- Unknown PGML block tokens that match common renderer errors.

### HTML and rendering safety

**`pgml_html_policy` (ERROR/WARNING)**
- Disallowed HTML tags anywhere in PGML or MODES HTML (table, script).
- Raw HTML in PGML text (span, style, br, img, a) outside safe pathways.
- Escaped HTML output (`&lt;div`, `&lt;span`) indicating render failures.
- tex2jax_ignore spans in output (suppressed MathJax).

### Answer and grading consistency

**`pgml_grading_consistency` (ERROR/WARNING)**
- Blanks without evaluators and ANS() without blanks.
- Reused answer variables across multiple blanks.
- Mapping mismatches in matching or dropdown patterns.
- Answer blanks inside solutions or hints.
- Context set after Compute/Formula calls.

### Randomization and stability

**`pgml_randomization_safety` (ERROR/WARNING)**
- Empty lists used in `random()`, `randomSubset`, or choice functions.
- Random ranges that can be zero or degenerate.
- Shuffles without inverse mappings in matching problems.
- Hash key order used as random ordering.

### Encoding and whitespace hygiene

**`pgml_encoding_policy` (WARNING)**
- NBSP and invisible control characters.
- Mojibake sequences (UTF-8/Latin-1 mixups).
- Unicode math symbols that should be LaTeX in PGML.
- Non-ASCII in header fields (copy/paste problems).

### Accessibility and clarity

**`pgml_accessibility_checks` (WARNING)**
- `<img>` without alt text.
- Color-only signals with no text cue in labels.
- Duplicate labels in matching or multiple choice layouts.

### Security and sandboxed behavior

**`pgml_security_sandbox` (ERROR/WARNING)**
- `system()`, backticks, or qx// command execution.
- Network calls or dynamic `require`.
- File writes or dangerous eval usage.

### Renderer-aligned heuristics (offline)

**`pgml_renderer_signal_bundle` (ERROR/WARNING)**
- Detect strings that match known renderer errors.
- Escaped HTML output signals.
- Empty BEGIN_PGML output.

### Common syntax mistakes (high value)

| Proposed ID | Detection idea | Severity | Notes |
| --- | --- | --- | --- |
| `pgml_unclosed_quote` | Unclosed single or double quotes in strings | ERROR | Perl compile error |
| `pgml_unclosed_paren` | Unbalanced parentheses in loadMacros or Context | ERROR | Perl compile error |
| `pgml_missing_semicolon` | Missing semicolon after statements | WARNING | Perl compile error |
| `pgml_comma_in_list` | Missing comma in loadMacros list | ERROR | Perl compile error |
| `pgml_bad_bracket_in_pgml` | `[` without `]` in PGML text lines | WARNING | PGML parse error |
| `pgml_bad_inline_marker` | Nested [@ inside [@ @] | WARNING | PGML parse error |
| `pgml_block_marker_indent` | BEGIN/END markers indented oddly | INFO | Style consistency |

### Imported .pl syntax pitfalls

| Proposed ID | Detection idea | Severity | Notes |
| --- | --- | --- | --- |
| `pgml_parser_popup_mismatch` | PopUp used but parserPopUp.pl missing | WARNING | Extend macro_rules |
| `pgml_parser_radio_mismatch` | RadioButtons used but parserRadioButtons.pl missing | WARNING | Extend macro_rules |
| `pgml_parser_checkbox_mismatch` | CheckboxList used but parserCheckboxList.pl missing | WARNING | Extend macro_rules |
| `pgml_nicetables_missing` | DataTable/LayoutTable without niceTables.pl | WARNING | Extend macro_rules |
| `pgml_numberwithunits_missing` | NumberWithUnits without parserNumberWithUnits.pl | WARNING | Extend macro_rules |
| `pgml_context_units_missing` | Context("Unit") without contextUnits.pl | WARNING | Extend macro_rules |
| `pgml_context_fraction_missing` | Context("Fraction") without contextFraction.pl | WARNING | Extend macro_rules |
| `pgml_draggable_subsets_missing` | DraggableSubsets without draggableSubsets.pl | WARNING | Extend macro_rules |

## Test strategy for new ideas

- Add unit tests per plugin in `tests/` with minimal `.pg` snippets.
- Include both positive and negative cases for each rule.
- Prefer exact message matching for critical rules, substring matching for noisy rules.
- For renderer-aligned heuristics, add fixture text that matches known error logs.

## Selection priorities

Use these to decide what to implement next:

1. Error class: rules that map to PGML parser errors or hard render failures.
2. High signal: low false positives, simple detection.
3. Coverage gaps: patterns not covered by existing plugins.
4. Testability: rules with short, deterministic test cases.
