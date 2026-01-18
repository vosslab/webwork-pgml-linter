# PGML Lint Architecture

This document describes the internal architecture of the PGML lint tool for contributors and maintainers.

## Overview

The linter is a Python-based static analysis tool that parses WeBWorK `.pg` files without requiring the PG library. It uses a modular plugin architecture where each check is implemented as a separate plugin.

## Module Structure

```
pgml_lint/
  __init__.py         # Package marker
  core.py             # Issue creation and formatting
  parser.py           # Text parsing utilities
  pgml.py             # PGML-specific parsing
  rules.py            # Default block/macro rules
  registry.py         # Plugin registration system
  engine.py           # Lint orchestration
  plugins/
    __init__.py       # Built-in plugin list
    *.py              # Individual plugins
```

## Data Flow

```
File Text
    |
    v
[parser.py] strip_comments() --> stripped_comments
    |
    v
[parser.py] strip_heredocs() --> stripped_text (for macro detection)
    |
    v
[engine.py] build_context() --> context dict
    |
    v
[engine.py] run_plugins() --> issues list
    |
    v
[core.py] format_issue() --> output
```

## Context Dictionary

The context dict is built by `engine.build_context()` and passed to all plugins. It contains:

| Key | Type | Description |
|-----|------|-------------|
| `file_path` | `str | None` | Path to the file being linted |
| `text` | `str` | Original file contents |
| `newlines` | `list[int]` | Positions of newline characters (for line number mapping) |
| `stripped_comments` | `str` | Text with Perl comments removed |
| `stripped_text` | `str` | Text with comments and heredoc bodies removed |
| `macros_loaded` | `set[str]` | Lowercased macro filenames from `loadMacros()` |
| `assigned_vars` | `set[str]` | Variable names that appear assigned |
| `uses_pgml` | `bool` | Whether PGML syntax is detected |
| `block_rules` | `list[dict]` | Block pairing rules |
| `macro_rules` | `list[dict]` | Macro requirement rules |
| `block_marker_issues` | `list[dict]` | Issues from block marker parsing |
| `pgml_regions` | `list[dict]` | All PGML regions (blocks + heredocs) |
| `pgml_block_regions` | `list[dict]` | PGML regions from BEGIN/END blocks |
| `pgml_heredoc_regions` | `list[dict]` | PGML regions from heredocs |
| `pgml_heredoc_issues` | `list[dict]` | Issues from heredoc parsing |

Plugins may add additional keys to the context for downstream plugins:

| Key | Added By | Description |
|-----|----------|-------------|
| `pgml_inline_spans` | `pgml_inline` | Inline code span positions per region |
| `pgml_blank_vars` | `pgml_blanks` | Variables referenced in PGML blanks |
| `pgml_blank_spans` | `pgml_blanks` | Blank marker positions per region |

## PGML Region Format

Each PGML region dict contains:

```python
{
    "start": int,     # Byte offset of region content start
    "end": int,       # Byte offset of region content end
    "kind": str,      # "BEGIN_PGML", "BEGIN_PGML_SOLUTION", "HEREDOC_PGML", etc.
    "line": int,      # Line number of region start
}
```

## Issue Format

Issues are dicts with:

```python
{
    "severity": str,  # "ERROR" or "WARNING"
    "message": str,   # Human-readable description
    "line": int,      # Optional: line number
    "plugin": str,    # Added by engine: plugin id
}
```

## Parser Utilities

### Comment Stripping

`parser.strip_comments(text)` removes Perl line comments (`#...`) while:
- Preserving strings (single and double quoted)
- Preserving heredoc bodies (comments inside heredocs are kept)

### Heredoc Detection

`parser._scan_heredoc_terminator(line)` detects heredoc introducers like:
- `<<END`
- `<<'END'`
- `<<"END"`
- `<<- END` (indented terminator)

### Line Number Mapping

`parser.build_newline_index(text)` builds a sorted list of newline positions.
`parser.pos_to_line(newlines, pos)` uses bisect to map byte offset to line number in O(log n).

### Macro Extraction

`parser.extract_loaded_macros(stripped_text)` finds `loadMacros(...)` calls and extracts quoted filenames.

### Variable Assignment Detection

`parser.extract_assigned_vars(stripped_text)` finds:
- Scalar declarations: `my $var`, `our $var`
- Scalar assignments: `$var =`
- Array declarations: `my @arr`, `our @arr`
- Array assignments: `@arr =`
- Hash declarations: `my %hash`, `our %hash`
- Hash assignments: `%hash =`

## PGML Parsing

### Inline Span Detection

`pgml.extract_inline_spans(block_text, start_offset, newlines)` finds `[@` ... `@]` pairs using a stack.

### Math Span Detection

`pgml._extract_math_spans(block_text)` finds:
- Display math: `` [`...`] ``
- Inline math: `[:...:+]` (with optional modifiers)

### Blank Detection

`pgml.scan_pgml_blanks(...)` finds `[_...]` patterns and extracts:
- Answer spec: `{$answer}` or `*{$answer}`
- Referenced variables from the spec

### Bracket Balance

`pgml.check_pgml_bracket_balance(...)` checks `[` and `]` balance while masking:
- Inline code spans
- Blank markers
- Math spans

## Plugin Registration

Plugins are registered via `registry.py`:

1. `BUILTIN_PLUGINS` in `plugins/__init__.py` lists module paths
2. `build_registry()` imports each module and reads:
   - `PLUGIN_ID`: Unique identifier
   - `PLUGIN_NAME`: Human-readable name
   - `DEFAULT_ENABLED`: Whether enabled by default
   - `run(context)`: The check function

## Adding a New Plugin

1. Create `pgml_lint/plugins/my_plugin.py`:

```python
PLUGIN_ID = "my_plugin"
PLUGIN_NAME = "My custom check"
DEFAULT_ENABLED = True

def run(context: dict) -> list[dict]:
    issues = []
    # Your analysis code
    return issues
```

2. Add to `BUILTIN_PLUGINS` in `pgml_lint/plugins/__init__.py`

3. Add tests in `tests/test_pgml_simple_lint.py`

## Testing

Run tests with:

```bash
python3 -m pytest tests/test_pyflakes.py tests/test_pgml_simple_lint.py -v
```

The test file `tests/test_pgml_simple_lint.py` uses `_run_lint(text)` helper to lint text snippets.
