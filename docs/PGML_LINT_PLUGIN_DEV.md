# PGML Lint Plugin Development Guide

This guide explains how to create custom plugins for the PGML linter.

## Plugin Basics

A plugin is a Python module that:
1. Defines metadata (ID, name, default enabled status)
2. Implements a `run(context)` function that returns issues

## Minimal Plugin Template

```python
# Standard Library
# (import as needed)

# Local modules
# import pgml_lint.parser  # if you need parsing utilities

PLUGIN_ID = "my_check"
PLUGIN_NAME = "My custom check"
DEFAULT_ENABLED = True  # or False for optional plugins


#============================================


def run(context: dict[str, object]) -> list[dict[str, object]]:
    """
    Check for a specific issue pattern.

    Args:
        context: Shared lint context with text, regions, etc.

    Returns:
        list[dict[str, object]]: List of issue dicts.
    """
    issues: list[dict[str, object]] = []

    # Your analysis code here

    return issues
```

## Context Available to Plugins

The `context` dict contains pre-parsed information:

### Text Content

```python
text = str(context.get("text", ""))              # Original file
stripped_text = str(context.get("stripped_text", ""))  # Comments/heredocs removed
```

### Line Number Mapping

```python
import pgml_lint.parser

newlines = context.get("newlines", [])
line_num = pgml_lint.parser.pos_to_line(newlines, byte_offset)
```

### Loaded Macros

```python
macros_loaded = context.get("macros_loaded", set())
if "pgml.pl" in macros_loaded:
    # PGML.pl is loaded
```

### Assigned Variables

```python
assigned_vars = context.get("assigned_vars", set())
if var_name in assigned_vars:
    # Variable is defined
```

### PGML Regions

```python
regions = context.get("pgml_regions", [])
for region in regions:
    start = int(region.get("start", 0))
    end = int(region.get("end", 0))
    kind = str(region.get("kind", ""))  # "BEGIN_PGML", "HEREDOC_PGML", etc.
    line = int(region.get("line", 0))
    block_text = text[start:end]
```

### Pre-computed Issues

Some issues are computed during context building:

```python
# Block marker issues (BEGIN/END mismatches)
block_issues = context.get("block_marker_issues", [])

# Heredoc terminator issues
heredoc_issues = context.get("pgml_heredoc_issues", [])
```

## Creating Issues

Issues are dicts with these fields:

```python
issue = {
    "severity": "ERROR",    # or "WARNING"
    "message": "Description of the problem",
    "line": 42,             # optional but recommended
}
issues.append(issue)
```

The engine automatically adds the `plugin` field with your `PLUGIN_ID`.

### Severity Guidelines

Use `ERROR` for:
- Syntax errors that will cause failures
- Mismatched block markers
- Unterminated constructs

Use `WARNING` for:
- Style issues
- Missing recommended elements
- Potentially problematic patterns

## Using Parser Utilities

Import the parser module for common operations:

```python
import pgml_lint.parser

# Build newline index for line number mapping
newlines = pgml_lint.parser.build_newline_index(text)

# Convert byte offset to line number
line = pgml_lint.parser.pos_to_line(newlines, offset)

# Find function calls with balanced parentheses
calls = pgml_lint.parser.iter_calls(stripped_text, {"myFunction"})
for call in calls:
    name = call["name"]       # Function name
    arg_text = call["arg_text"]  # Arguments between parens
    line = call["line"]       # Line number
```

## Using PGML Utilities

Import the pgml module for PGML-specific parsing:

```python
import pgml_lint.pgml

# Extract inline code spans [@ ... @]
inline_issues, inline_spans = pgml_lint.pgml.extract_inline_spans(
    block_text, start_offset, newlines
)

# Scan PGML blanks [_...]{$var}
blank_issues, vars_found, blank_spans = pgml_lint.pgml.scan_pgml_blanks(
    block_text, start_offset, newlines, inline_spans
)

# Check bracket balance
bracket_issues = pgml_lint.pgml.check_pgml_bracket_balance(
    block_text, start_offset, newlines, inline_spans, blank_spans
)
```

## Sharing Data Between Plugins

Plugins can add keys to the context for downstream plugins:

```python
def run(context: dict[str, object]) -> list[dict[str, object]]:
    issues = []

    # Compute something
    my_data = analyze_something(context)

    # Share with downstream plugins
    context["my_plugin_data"] = my_data

    return issues
```

Example from `pgml_inline` plugin:

```python
# Store inline spans for use by pgml_blanks and pgml_brackets
context["pgml_inline_spans"] = inline_spans_by_region
```

## Example: Check for Missing Solution

```python
import re

PLUGIN_ID = "missing_solution"
PLUGIN_NAME = "Check for missing PGML_SOLUTION"
DEFAULT_ENABLED = False  # Optional check


def run(context: dict[str, object]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []

    # Only check files that use PGML
    if not context.get("uses_pgml"):
        return issues

    text = str(context.get("text", ""))

    # Check for BEGIN_PGML_SOLUTION
    if "BEGIN_PGML_SOLUTION" not in text:
        # Also check for old-style SOLUTION
        if "BEGIN_SOLUTION" not in text:
            issue = {
                "severity": "WARNING",
                "message": "PGML file has no solution block",
            }
            issues.append(issue)

    return issues
```

## Example: Check for Deprecated Functions

```python
import re
import pgml_lint.parser

PLUGIN_ID = "deprecated_functions"
PLUGIN_NAME = "Check for deprecated function calls"
DEFAULT_ENABLED = True

DEPRECATED = {
    "ANS_NUM_CMP": "Use Compute()->cmp instead",
    "std_num_cmp": "Use Compute()->cmp instead",
}


def run(context: dict[str, object]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    text = str(context.get("stripped_text", ""))
    newlines = context.get("newlines", [])

    for func_name, suggestion in DEPRECATED.items():
        pattern = r"\b" + re.escape(func_name) + r"\s*\("
        for match in re.finditer(pattern, text):
            line = pgml_lint.parser.pos_to_line(newlines, match.start())
            message = f"{func_name} is deprecated. {suggestion}"
            issue = {
                "severity": "WARNING",
                "message": message,
                "line": line,
            }
            issues.append(issue)

    return issues
```

## Registering Built-in Plugins

To add a plugin to the built-in set:

1. Create the plugin file: `pgml_lint/plugins/my_plugin.py`

2. Add to `BUILTIN_PLUGINS` in `pgml_lint/plugins/__init__.py`:

```python
BUILTIN_PLUGINS = [
    # ... existing plugins ...
    "pgml_lint.plugins.my_plugin",
]
```

## Loading External Plugins

Users can load plugins from external files:

```bash
python3 tools/webwork_pgml_simple_lint.py --plugin my_plugin.py -d problems/
```

The plugin file must be a valid Python module with the required attributes.

## Testing Plugins

Add tests to `tests/test_pgml_simple_lint.py`:

```python
def test_my_plugin_detects_issue() -> None:
    text = """DOCUMENT();
loadMacros('PGML.pl');
BEGIN_PGML
[problematic content here]
END_PGML
ENDDOCUMENT();
"""
    issues = _run_lint(text)
    assert any("expected message" in issue["message"] for issue in issues)


def test_my_plugin_no_false_positive() -> None:
    text = """DOCUMENT();
loadMacros('PGML.pl');
BEGIN_PGML
[correct content here]
END_PGML
ENDDOCUMENT();
"""
    issues = _run_lint(text)
    assert not any("expected message" in issue["message"] for issue in issues)
```

## Plugin Best Practices

1. **Be specific**: Check for exact patterns, not broad matches
2. **Avoid false positives**: When in doubt, don't report
3. **Provide helpful messages**: Include what was expected and why
4. **Include line numbers**: Makes issues actionable
5. **Handle edge cases**: Empty files, missing regions, etc.
6. **Document your plugin**: What it checks and why
7. **Consider making optional**: If the check is noisy, set `DEFAULT_ENABLED = False`
