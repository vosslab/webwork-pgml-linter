# PGML Lint Concepts

This document explains the PGML syntax concepts that the linter validates.

## PGML Overview

PGML (PG Markup Language) is a lightweight markup language used in WeBWorK for creating problem content. It provides a cleaner syntax than raw Perl/PG for common operations.

## PGML Blocks

PGML content is enclosed in block markers:

```perl
BEGIN_PGML
Your PGML content here.
END_PGML
```

### Block Types

| Marker | Purpose |
|--------|---------|
| `BEGIN_PGML` / `END_PGML` | Main problem content |
| `BEGIN_PGML_SOLUTION` / `END_PGML_SOLUTION` | Solution shown after due date |
| `BEGIN_PGML_HINT` / `END_PGML_HINT` | Hints shown on request |

**Lint Check:** The linter verifies block markers are properly paired and not nested inappropriately.

## PGML Heredocs

PGML can also be used via heredoc syntax:

```perl
$text = PGML::Format(<<END_PGML);
Your PGML content here.
END_PGML
```

**Lint Check:** The linter detects unterminated PGML heredocs.

## Answer Blanks

PGML answer blanks use bracket-underscore syntax:

```
[_]{$answer}      # Basic blank
[___]{$answer}    # Wider blank
[________]{$answer}  # Even wider blank
```

The width is visual only; any number of underscores works.

### Answer Specs

The braces contain the expected answer:

```
[_]{$answer}           # Variable reference
[_]{Compute("x^2")}    # Inline computation
[_]{Real(42)}          # Literal value
[_]{$ans->cmp}         # With custom checker
```

### Star Specs

A star spec provides grading options:

```
[_]*{$answer}          # Star spec only
[_]{$answer}*{cmp}     # Both payload and star (unusual)
```

**Lint Checks:**
- Missing answer spec: `[_]` without `{...}`
- Empty spec: `[_]{}`
- Unbalanced braces in spec
- Variables referenced but not assigned

## Inline Code

Perl code can be embedded inline:

```
The value is [@ $var @].
The answer is [@ sprintf("%.2f", $value) @].
```

The star modifier suppresses paragraph wrapping:

```
[@ image("graph.png") @]*
```

**Lint Check:** The linter verifies `[@` and `@]` are properly paired.

## Math Delimiters

PGML provides special delimiters for LaTeX math:

### Display Math

```
[` x^2 + y^2 = r^2 `]
```

Renders as centered, display-style math.

### Inline Math

```
The formula [:x^2:] shows...
```

With modifiers:
```
[:x^2:+]   # Forces display style
[:x^2:*]   # Variant rendering
```

**Note:** The bracket checker excludes math delimiters to avoid false positives from LaTeX content like interval notation `[0, 2\pi)`.

## Variable Interpolation

Variables can be interpolated into PGML:

```perl
$a = 5;
$b = 3;

BEGIN_PGML
What is [$a] + [$b]?
END_PGML
```

This renders as "What is 5 + 3?"

## loadMacros

WeBWorK problems load functionality via macros:

```perl
loadMacros(
    'PGstandard.pl',
    'PGML.pl',
    'MathObjects.pl',
    'PGcourse.pl',
);
```

**Lint Check:** The linter verifies required macros are loaded for functions used:
- PGML syntax requires `PGML.pl`
- `Context()`, `Compute()` require `MathObjects.pl` (or `PGML.pl` which loads it)
- `DataTable()` requires `niceTables.pl`
- etc.

## DOCUMENT Structure

Standard WeBWorK problem structure:

```perl
DOCUMENT();

loadMacros(
    'PGstandard.pl',
    'PGML.pl',
);

# Setup code here

BEGIN_PGML
Problem content here.
END_PGML

ENDDOCUMENT();
```

**Lint Check:** The linter verifies `DOCUMENT()` and `ENDDOCUMENT()` are properly paired.

## Common Patterns

### Simple Numeric Answer

```perl
$answer = Compute("42");

BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML
```

### Multiple Blanks

```perl
$a = random(1, 10);
$b = random(1, 10);
$sum = $a + $b;
$product = $a * $b;

BEGIN_PGML
Given [`a = [$a]`] and [`b = [$b]`]:

Sum: [_]{$sum}

Product: [_]{$product}
END_PGML
```

### Array of Answers

```perl
@answers = (
    Compute("1"),
    Compute("4"),
    Compute("9"),
);

BEGIN_PGML
1. [_]{$answers[0]}
2. [_]{$answers[1]}
3. [_]{$answers[2]}
END_PGML
```

**Note:** The linter recognizes array assignments (`@answers =`) to avoid false warnings about `$answers`.

### Inline Images

```perl
BEGIN_PGML
[@ image("graph.png", width => 300) @]*
END_PGML
```

### Tables

```perl
loadMacros('niceTables.pl');

BEGIN_PGML
[@ DataTable([
    ["x", "y"],
    [1, 2],
    [3, 4],
]) @]*
END_PGML
```

### Multiple Choice

```perl
loadMacros('parserRadioButtons.pl');

$mc = RadioButtons(
    ["Choice A", "Choice B", "Choice C"],
    "Choice A"  # Correct answer
);

BEGIN_PGML
Select the best answer:

[_]{$mc}
END_PGML
```

## What the Linter Cannot Check

The linter performs static analysis without executing Perl. It cannot:

1. **Verify runtime values**: Whether `$answer` contains a valid MathObject
2. **Check Perl syntax**: The linter doesn't parse Perl, only pattern-matches
3. **Validate math expressions**: Whether LaTeX is correct
4. **Check problem logic**: Whether the problem makes sense
5. **Verify file includes**: Whether `includePGproblem()` targets exist
6. **Track control flow**: Variables defined in conditionals

## False Positives

The linter may produce false positives for:

1. **Complex variable patterns**: Variables created via method calls, complex dereferencing
2. **Dynamic content**: Variables defined based on runtime conditions
3. **Unusual syntax**: Non-standard but valid PGML patterns
4. **Intentional patterns**: Documented examples showing incorrect syntax

Use `--disable` to suppress noisy checks for your codebase.

## False Negatives

The linter may miss issues:

1. **Perl syntax errors**: Not a Perl parser
2. **Logic errors**: Cannot understand problem intent
3. **Runtime failures**: Requires execution to detect
4. **Complex nesting**: May miss deeply nested issues

The linter is a first-pass tool to catch common issues, not a substitute for testing.
