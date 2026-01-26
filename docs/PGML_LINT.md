# PGML Lint Tool

`tools/webwork_pgml_simple_lint.py` is a static analysis tool for WeBWorK `.pg` files with PGML validation. It works offline without requiring the PG library.

## Purpose

**This linter enforces modern PGML standards and flags legacy PG syntax.** It helps:
- Identify deprecated patterns (e.g., BEGIN_TEXT blocks, mixed answer styles)
- Ensure compliance with modern PGML best practices
- Detect common authoring mistakes in PGML markup
- Migrate legacy PG files to clean, maintainable PGML

If you're maintaining older PG files, this linter will highlight areas that should be updated to modern PGML syntax.

## Quick Start

```bash
# Check a single file
python3 tools/webwork_pgml_simple_lint.py -i path/to/file.pg

# Check all .pg files in a directory
python3 tools/webwork_pgml_simple_lint.py -d problems/

# Verbose output (shows what checks are running and context excerpts)
python3 tools/webwork_pgml_simple_lint.py -v -i file.pg

# Quiet mode (only errors/warnings, no summary)
python3 tools/webwork_pgml_simple_lint.py -q -d problems/
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-i`, `--input FILE` | Check a single .pg file |
| `-d`, `--directory DIR` | Check all .pg files in directory (default: current) |
| `-v`, `--verbose` | Show more details (plugin ids and excerpts when available) |
| `-q`, `--quiet` | Only show problems, no summary |

## What the Linter Checks

### PGML Block Structure

**BEGIN/END block pairing** (`block_markers` plugin)
- Detects unmatched `BEGIN_PGML`, `END_PGML`, `BEGIN_PGML_SOLUTION`, etc.
- Reports nested PGML blocks (e.g., `BEGIN_PGML_HINT` inside `BEGIN_PGML`)
- Example error: `END_PGML without matching BEGIN`

**DOCUMENT pairing** (`document_pairs` plugin)
- Checks `DOCUMENT()` and `ENDDOCUMENT()` are properly paired
- Example error: `DOCUMENT() count does not match ENDDOCUMENT()`

**PGML heredoc terminators** (`pgml_heredocs` plugin)
- Detects unterminated PGML heredocs like `PGML::Format(<<END_PGML)`
- Example error: `PGML heredoc terminator 'END_PGML' not found`

**PG header tags** (`pgml_header_tags` plugin)
- Checks DESCRIPTION/ENDDESCRIPTION and KEYWORDS metadata
- Flags missing DBsubject/DBchapter/DBsection and placeholder values

**Deprecated TEXT blocks** (`pgml_text_blocks` plugin)
- Flags legacy `BEGIN_TEXT/END_TEXT` blocks that should be migrated to PGML
- Example warning: `BEGIN_TEXT is deprecated legacy PG syntax; use BEGIN_PGML with PGML.pl for modern WebWork problems`

**Raw HTML in PGML** (`pgml_html_in_text` plugin)
- Detects HTML tags and entities in PGML text that will be stripped or mangled
- Flags `<strong>`, `<em>`, `<br>`, `<sub>`, `<sup>`, `<span>`, `<style>`, HTML entities
- Suggests PGML or LaTeX alternatives

**HTML policy checks** (`pgml_html_policy` plugin)
- Flags disallowed tags like `<script>`, `<iframe>`, `<object>`, `<embed>`
- Flags table tags outside PGML blocks (for example in MODES HTML)
- Warns on inline `<style>` tags outside HEADER_TEXT and tex2jax_ignore usage
- Warns on disallowed tags used inside PGML tag wrappers

**TeX color commands** (`pgml_tex_color` plugin)
- Warns when `\color{...}` or `\textcolor{...}` appears in PG content
- Suggests PGML tag wrappers or HTML spans instead

**Forbidden table tags** (`pgml_html_forbidden_tags` plugin)
- Errors on `<table>`, `<tr>`, `<td>`, `<th>` and related tags anywhere in PGML blocks
- Suggests `DataTable()` or `LayoutTable()` from `niceTables.pl`

**HTML div tags** (`pgml_html_div` plugin)
- Flags any `<div>` tags (including escaped ones) found in PGML blocks
- Useful when div output indicates broken rendering or HTML escaping

**Non-breaking spaces** (`pgml_nbsp` plugin)
- Warns on Unicode non-breaking spaces (U+00A0, U+202F) that affect layout

**Mojibake/encoding glitches** (`pgml_mojibake` plugin)
- Flags UTF-8/Latin-1 encoding glitches that show up as garbled characters
- Includes common mojibake markers like U+00C2, U+00C3, or U+00E2 U+0080 U+0099 sequences

**Legacy ans_rule()** (`pgml_ans_rule` plugin)
- Detects old-style `ans_rule()` function calls
- Suggests using PGML inline answer blanks `[_]{$answer}` instead

**Legacy $BR variable** (`pgml_br_variable` plugin)
- Detects old-style `$BR` line break variable
- Suggests using blank lines in PGML for paragraph breaks

**MODES HTML escaping** (`pgml_modes_html_escape` plugin)
- Detects when HTML from `MODES()` is incorrectly used with `[$var]` interpolation
- Warns that `[$var]` escapes HTML; should use `[@ $var @]*` instead
- Prevents subtle bug where HTML appears as escaped text

**Legacy answer checkers** (`pgml_old_answer_checkers` plugin)
- Detects deprecated `num_cmp()`, `str_cmp()`, `fun_cmp()` functions
- Suggests using MathObjects with `->cmp()` method instead

**Legacy SOLUTION/HINT macros** (`pgml_solution_hint_macros` plugin)
- Detects deprecated `SOLUTION(EV3(<<'END'))` and `HINT(EV3(<<'END'))` patterns
- Suggests using `BEGIN_PGML_SOLUTION` and `BEGIN_PGML_HINT` blocks instead

### PGML Syntax

**Inline code markers** (`pgml_inline` plugin)
- Checks `[@` and `@]` pairs are balanced
- Example warning: `PGML inline open [@ without matching @]`

**PGML parse hazards** (`pgml_pgml_parse_hazards` plugin)
- Flags unknown PGML block tokens like `[balance]`
- Warns when `[@ @]` inline code has unbalanced parentheses

**PGML wrappers in strings** (`pgml_pgml_wrapper_in_string` plugin)
- Warns when PGML tag wrapper syntax appears inside Perl strings

**MODES in inline eval** (`pgml_modes_in_inline` plugin)
- Warns when MODES() appears inside `[@ @]` blocks

**Inline PGML syntax** (`pgml_inline_pgml_syntax` plugin)
- Flags PGML tag wrapper syntax inside `[@ ... @]*` blocks
- Example error: `PGML tag wrapper syntax found inside [@ @] block`

**Inline brace balance** (`pgml_inline_braces` plugin)
- Checks `{` and `}` are balanced inside `[@ ... @]*` blocks
- Example error: `PGML inline code has unclosed '{' brace`

**Answer blank syntax** (`pgml_blanks` plugin)
- Detects blanks missing answer specs: `[_]` without `{$answer}`
- Checks for unbalanced braces in blank specs
- Example warning: `PGML blank missing answer spec`

**Underscore emphasis balance** (`pgml_underscore_emphasis` plugin)
- Warns when underscore emphasis markers are not closed before paragraph ends

**Bracket balance** (`pgml_brackets` plugin, disabled by default)
- Checks `[` and `]` balance in PGML content
- Disabled by default because plain brackets are common in math text

### Macro and Variable Checks

**Required macros** (`pgml_required_macros` plugin)
- Warns when PGML syntax is used without loading `PGML.pl`
- Example warning: `PGML used without required macros: pgml.pl`

**loadMacros integrity** (`pgml_loadmacros_integrity` plugin)
- Flags missing parentheses or semicolons in loadMacros blocks
- Warns on empty macro lists and missing commas

**Macro rule coverage** (`macro_rules` plugin)
- Detects functions used without required macro files
- Examples:
  - `Context()` / `Compute()` require `MathObjects.pl` or `PGML.pl`
  - `RadioButtons()` requires `parserRadioButtons.pl`
  - `DropDown()` requires `parserPopUp.pl` or `PGchoicemacros.pl`
  - `MultiAnswer()` requires `parserMultiAnswer.pl`
  - `OneOf()` requires `parserOneOf.pl`
  - `NchooseK()` requires `PGchoicemacros.pl`
  - `FormulaUpToConstant()` requires `parserFormulaUpToConstant.pl`
  - `DataTable()` requires `niceTables.pl`

**Function signatures** (`pgml_function_signatures` plugin)
- Checks expected argument counts for common PG functions
- Warns on known function name typos

**Variable assignment checking** (`pgml_blank_assignments` plugin)
- Warns when PGML blanks reference undefined variables
- Recognizes scalar (`$var`), array (`@arr`), and hash (`%hash`) assignments
- Example warning: `PGML blank references $ans without assignment in file`

**HTML variable passthrough** (`pgml_html_var_passthrough` plugin)
- Warns when HTML stored in variables is output without `[$var]*` passthrough

**includePGproblem usage** (`pgml_include_pgproblem` plugin)
- Warns when `includePGproblem()` is used because the target file is not verified
- Flags include-only stubs that contain no local content

**Extreme line length** (`pgml_line_length` plugin)
- Warns on lines longer than 200 characters, with extra warnings over 400

**Embedded blob payloads** (`pgml_blob_payloads` plugin)
- Flags base64-like blobs or ggbbase64 markers embedded in PG files

**Span HTML interpolation** (`pgml_span_interpolation` plugin)
- Warns when variables containing `<span>` HTML are not interpolated with `[$var]` in PGML

**Label dot trap** (`pgml_label_dot` plugin)
- Warns when labels are built as `A.` which can trigger PGML list parsing

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No errors found |
| 1 | Errors found |

## What Gets Checked

The linter runs these checks automatically:

| Check | Description |
|-------|-------------|
| Block pairing | BEGIN_PGML/END_PGML properly matched |
| Heredoc terminators | PGML heredocs properly closed |
| DOCUMENT pairing | DOCUMENT()/ENDDOCUMENT() balanced |
| Deprecated TEXT blocks | Flags legacy BEGIN_TEXT/END_TEXT syntax |
| Required macros | PGML.pl loaded when PGML is used |
| loadMacros integrity | loadMacros syntax pitfalls |
| Macro coverage | Functions have required macro files |
| Function signatures | Expected argument counts and typos |
| Inline markers | [@ @] code blocks properly paired |
| PGML parse hazards | Unknown block tokens and inline paren balance |
| PGML wrappers in strings | PGML tag wrappers inside Perl strings |
| MODES in inline eval | MODES() inside [@ @] blocks |
| Inline PGML syntax | Inline code does not emit PGML wrappers |
| Inline brace balance | Inline code braces are balanced |
| Blank syntax | Answer blanks have proper specs |
| Underscore emphasis | Underscore markers closed before paragraph ends |
| Raw HTML in PGML | Flags raw HTML tags and entities in PGML text |
| TeX color commands | Warns on \\color and \\textcolor usage |
| HTML policy | Disallowed HTML tags and table tags outside PGML |
| Forbidden HTML tags | Forbids table-related tags in PGML blocks |
| HTML div tags | Flags div tags and escaped div output |
| Non-breaking spaces | Detects Unicode NBSP characters |
| Mojibake sequences | Flags encoding glitch sequences |
| Variable references | Blanks don't reference undefined variables |
| Span interpolation | Span HTML variables appear as [$var] in PGML |
| HTML variable passthrough | HTML vars require [$var]* output |
| Label dot trap | Warns on A. label generation in Perl |
| Answer style consistency | Detects mixed PGML/ANS() styles |
| Header tags | Checks DESCRIPTION/KEYWORDS and DB metadata |
| includePGproblem usage | Warns when content is delegated to includes |
| Line length | Warns on extreme long lines |
| Blob payloads | Flags base64-like embedded payloads |

## For Developers

See [PGML_LINT_ARCHITECTURE.md](PGML_LINT_ARCHITECTURE.md) for internal architecture and [PGML_LINT_PLUGIN_DEV.md](PGML_LINT_PLUGIN_DEV.md) for writing custom plugins.
