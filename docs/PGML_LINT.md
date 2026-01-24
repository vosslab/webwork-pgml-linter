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

# Verbose output (shows what checks are running)
python3 tools/webwork_pgml_simple_lint.py -v -i file.pg

# Quiet mode (only errors/warnings, no summary)
python3 tools/webwork_pgml_simple_lint.py -q -d problems/
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-i`, `--input FILE` | Check a single .pg file |
| `-d`, `--directory DIR` | Check all .pg files in directory (default: current) |
| `-v`, `--verbose` | Show more details |
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

**Deprecated TEXT blocks** (`pgml_text_blocks` plugin)
- Flags legacy `BEGIN_TEXT/END_TEXT` blocks that should be migrated to PGML
- Example warning: `BEGIN_TEXT is deprecated legacy PG syntax; use BEGIN_PGML with PGML.pl for modern WebWork problems`

**Raw HTML in PGML** (`pgml_html_in_text` plugin)
- Detects HTML tags and entities in PGML text that will be stripped or mangled
- Flags `<strong>`, `<em>`, `<br>`, `<sub>`, `<sup>`, table tags, HTML entities
- Suggests PGML or LaTeX alternatives

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

**Answer blank syntax** (`pgml_blanks` plugin)
- Detects blanks missing answer specs: `[_]` without `{$answer}`
- Checks for unbalanced braces in blank specs
- Example warning: `PGML blank missing answer spec`

**Bracket balance** (`pgml_brackets` plugin, disabled by default)
- Checks `[` and `]` balance in PGML content
- Disabled by default because plain brackets are common in math text

### Macro and Variable Checks

**Required macros** (`pgml_required_macros` plugin)
- Warns when PGML syntax is used without loading `PGML.pl`
- Example warning: `PGML used without required macros: pgml.pl`

**Macro rule coverage** (`macro_rules` plugin)
- Detects functions used without required macro files
- Examples:
  - `Context()` / `Compute()` require `MathObjects.pl` or `PGML.pl`
  - `RadioButtons()` requires `parserRadioButtons.pl`
  - `DataTable()` requires `niceTables.pl`

**Variable assignment checking** (`pgml_blank_assignments` plugin)
- Warns when PGML blanks reference undefined variables
- Recognizes scalar (`$var`), array (`@arr`), and hash (`%hash`) assignments
- Example warning: `PGML blank references $ans without assignment in file`

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
| Macro coverage | Functions have required macro files |
| Inline markers | [@ @] code blocks properly paired |
| Blank syntax | Answer blanks have proper specs |
| Variable references | Blanks don't reference undefined variables |
| Answer style consistency | Detects mixed PGML/ANS() styles |

## For Developers

See [PGML_LINT_ARCHITECTURE.md](PGML_LINT_ARCHITECTURE.md) for internal architecture and [PGML_LINT_PLUGIN_DEV.md](PGML_LINT_PLUGIN_DEV.md) for writing custom plugins.
