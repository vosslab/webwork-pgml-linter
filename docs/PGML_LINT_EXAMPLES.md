# PGML Lint Examples: Good vs Bad

This document provides side-by-side examples of correct (Good) and incorrect (Bad) PGML code patterns for each lint rule. Use this as a quick reference guide when writing WeBWorK problems.

## Table of Contents

- [Block Markers](#block-markers)
- [PGML Heredocs](#pgml-heredocs)
- [Document Pairs](#document-pairs)
- [Required Macros](#required-macros)
- [Macro Requirements](#macro-requirements)
- [PGML Inline Markers](#pgml-inline-markers)
- [PGML Answer Blanks](#pgml-answer-blanks)
- [PGML Brackets](#pgml-brackets)
- [Variable Assignments](#variable-assignments)
- [Answer Style Consistency](#answer-style-consistency)

---

## Block Markers

**Rule:** `block_markers` - BEGIN/END block markers must be properly paired.

### Good

```perl
BEGIN_PGML
This is PGML content.
END_PGML
```

```perl
BEGIN_PGML_SOLUTION
This is the solution.
END_PGML_SOLUTION
```

```perl
BEGIN_TEXT
This is old-style TEXT.
END_TEXT
```

### Bad

```perl
BEGIN_PGML
This is PGML content.
# Missing END_PGML
```

```perl
BEGIN_PGML
This is PGML content.
END_TEXT  # Mismatched: should be END_PGML
```

```perl
BEGIN_PGML
Some content.
BEGIN_PGML_HINT  # Nested PGML blocks not allowed
Hint here.
END_PGML_HINT
END_PGML
```

---

## PGML Heredocs

**Rule:** `pgml_heredocs` - PGML heredoc blocks must have matching terminators.

### Good

```perl
$text = PGML::Format(<<END_PGML);
This is a PGML heredoc.
END_PGML
```

```perl
$hint = PGML::Format(<<'END_PGML_HINT');
This is a hint in a heredoc.
END_PGML_HINT
```

### Bad

```perl
$text = PGML::Format(<<END_PGML);
This is a PGML heredoc.
# Missing END_PGML terminator
```

```perl
$text = PGML::Format(<<END_PGML);
This is a PGML heredoc.
END_PGML_TYPO  # Terminator doesn't match
```

---

## Document Pairs

**Rule:** `document_pairs` - Every DOCUMENT() must have matching ENDDOCUMENT().

### Good

```perl
DOCUMENT();

loadMacros("PGML.pl");

BEGIN_PGML
Content here.
END_PGML

ENDDOCUMENT();
```

### Bad

```perl
DOCUMENT();

loadMacros("PGML.pl");

BEGIN_PGML
Content here.
END_PGML

# Missing ENDDOCUMENT()
```

```perl
# Missing DOCUMENT()

loadMacros("PGML.pl");

BEGIN_PGML
Content here.
END_PGML

ENDDOCUMENT();
```

```perl
loadMacros("PGML.pl");

ENDDOCUMENT();  # Appears before DOCUMENT()

DOCUMENT();
```

---

## Required Macros

**Rule:** `pgml_required_macros` - PGML syntax requires loading PGML.pl.

### Good

```perl
DOCUMENT();

loadMacros(
  "PGstandard.pl",
  "PGML.pl",  # Required for BEGIN_PGML
  "PGcourse.pl",
);

BEGIN_PGML
Content here.
END_PGML

ENDDOCUMENT();
```

### Bad

```perl
DOCUMENT();

loadMacros(
  "PGstandard.pl",
  "PGcourse.pl",
  # Missing PGML.pl
);

BEGIN_PGML  # ERROR: Using PGML without loading PGML.pl
Content here.
END_PGML

ENDDOCUMENT();
```

---

## Macro Requirements

**Rule:** `macro_rules` - Functions require their corresponding macro files.

### Good - MathObjects

```perl
loadMacros("PGML.pl");  # PGML.pl loads MathObjects.pl internally

$answer = Real(42);
$formula = Formula("x^2 + 1");

BEGIN_PGML
...
END_PGML
```

### Good - RadioButtons

```perl
loadMacros(
  "PGML.pl",
  "parserRadioButtons.pl",  # Required for RadioButtons
);

$rb = RadioButtons(["A", "B", "C"], "A");
```

### Good - DataTable

```perl
loadMacros(
  "PGML.pl",
  "niceTables.pl",  # Required for DataTable
);

$table = DataTable([["A", "B"], ["C", "D"]]);
```

### Bad

```perl
loadMacros("PGML.pl");

# Missing parserRadioButtons.pl
$rb = RadioButtons(["A", "B"], "A");  # ERROR
```

```perl
loadMacros("PGML.pl");

# Missing niceTables.pl
$table = DataTable([["x", "y"]]);  # ERROR
```

---

## PGML Inline Markers

**Rule:** `pgml_inline` - PGML inline code markers `[@` must match with `@]`.

### Good

```perl
BEGIN_PGML
The answer is [@ $value @].

The table is [@ DataTable(...) @]*.
END_PGML
```

### Bad

```perl
BEGIN_PGML
The answer is [@ $value.  # Missing @]
END_PGML
```

```perl
BEGIN_PGML
The answer is $value @].  # Missing [@
END_PGML
```

---

## PGML Answer Blanks

**Rule:** `pgml_blanks` - PGML answer blanks must have proper answer specifications.

### Good

```perl
$answer = Real(42);

BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML
```

```perl
$answer = Real(3.14);

BEGIN_PGML
Wider blank: [_____]{$answer}
END_PGML
```

```perl
$rb = RadioButtons(["A", "B"], "A");

BEGIN_PGML
[_]{$rb}
END_PGML
```

### Bad

```perl
BEGIN_PGML
What is the answer?

[_]  # Missing answer spec {$answer}
END_PGML
```

```perl
BEGIN_PGML
What is the answer?

[_]{}  # Empty answer spec
END_PGML
```

```perl
BEGIN_PGML
What is the answer?

[_]{$answer  # Unbalanced braces
END_PGML
```

---

## PGML Brackets

**Rule:** `pgml_brackets` (disabled by default) - Brackets should be balanced.

This rule is disabled because plain brackets are common in PGML text (interval notation, documentation).

### Examples That Would Trigger (if enabled)

```perl
BEGIN_PGML
The interval (5, 10] is half-open.  # Unbalanced: ( vs ]
END_PGML
```

**Note:** If you enable this rule, ensure you're not using plain brackets in mathematical notation or prose.

---

## Variable Assignments

**Rule:** `pgml_blank_assignments` - Variables used in PGML blanks should be assigned.

### Good

```perl
$answer = Real(42);  # Variable is assigned

BEGIN_PGML
What is 6 times 7?

[_]{$answer}  # Uses assigned variable
END_PGML
```

```perl
@choices = ("A", "B", "C");
$rb = RadioButtons(\@choices, "A");

BEGIN_PGML
[_]{$rb}
END_PGML
```

### Bad

```perl
# No assignment for $answer

BEGIN_PGML
What is 6 times 7?

[_]{$answer}  # ERROR: $answer not assigned
END_PGML
```

**Note:** This rule may produce false positives for variables assigned in ways the linter doesn't recognize (e.g., `my ($a, $b) = @_`). In those cases, consider disabling this rule for specific files.

---

## Answer Style Consistency

**Rule:** `pgml_ans_style` - Use pure PGML answer style, not mixed styles.

### Good - Pure PGML Style

```perl
$answer = Real(42);

BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML

ENDDOCUMENT();
```

```perl
$rb = RadioButtons(["True", "False"], "True");

BEGIN_PGML
Is PGML better than TEXT?

[_]{$rb}
END_PGML

ENDDOCUMENT();
```

```perl
$popup = PopUp(["?", "A", "B"], "A");

BEGIN_PGML
Select the correct answer: [_]{$popup}
END_PGML

ENDDOCUMENT();
```

### Bad - Mixed Style (Old PG + PGML)

```perl
$answer = Real(42);

BEGIN_PGML
What is 6 times 7?

[_______]  # Blank without answer spec
END_PGML

ANS($answer->cmp());  # ERROR: Using ANS() after PGML

ENDDOCUMENT();
```

```perl
$rb = RadioButtons(["A", "B"], "A");

BEGIN_PGML
[@ $rb->buttons() @]*  # Just displaying buttons
END_PGML

ANS($rb->cmp());  # ERROR: Mixed style

ENDDOCUMENT();
```

### Why This Matters

- **Pure PGML style** keeps answer specs inline with the question text
- **Old PG style** separates display from grading using `ANS()` calls
- Mixing these styles makes code harder to maintain and understand
- PGML is the modern, recommended approach

### How to Fix Mixed Style

Replace this pattern:
```perl
BEGIN_PGML
[@ $rb->buttons() @]*
END_PGML
ANS($rb->cmp());
```

With this:
```perl
BEGIN_PGML
[_]{$rb}
END_PGML
```

---

## Quick Reference: Common Patterns

### Text Input

```perl
# Good
$ans = Real(42);
BEGIN_PGML
Answer: [_]{$ans}
END_PGML

# Bad
BEGIN_PGML
Answer: [_]
END_PGML
ANS($ans->cmp());
```

### Multiple Choice (RadioButtons)

```perl
# Good
$rb = RadioButtons(["A", "B", "C"], "B");
BEGIN_PGML
[_]{$rb}
END_PGML

# Bad
BEGIN_PGML
[@ $rb->buttons() @]*
END_PGML
ANS($rb->cmp());
```

### Popup

```perl
# Good
$popup = PopUp(["?", "Yes", "No"], "Yes");
BEGIN_PGML
Choose: [_]{$popup}
END_PGML

# Bad
BEGIN_PGML
Choose: [@ $popup->menu() @]*
END_PGML
ANS($popup->cmp());
```

### Checkbox

```perl
# Good
$cb = CheckboxList(["A", "B", "C"], ["A", "C"]);
BEGIN_PGML
[_]{$cb}
END_PGML

# Bad
BEGIN_PGML
[@ $cb->buttons() @]*
END_PGML
ANS($cb->cmp());
```

---

## See Also

- [docs/PGML_LINT_PLUGINS.md](PGML_LINT_PLUGINS.md) - Detailed plugin reference
- [docs/PGML_LINT.md](PGML_LINT.md) - Usage guide and quick start
- [docs/PGML_LINT_CONCEPTS.md](PGML_LINT_CONCEPTS.md) - PGML syntax concepts
