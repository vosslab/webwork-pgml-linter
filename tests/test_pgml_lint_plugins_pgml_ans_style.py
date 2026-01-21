# Local modules
import pgml_lint.plugins.pgml_ans_style


#============================================

def test_run_warns_when_ans_after_end_pgml() -> None:
	text = """DOCUMENT();
loadMacros("PGML.pl");

$answer = Real(42);

BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML

ANS($answer->cmp());

ENDDOCUMENT();
"""
	newlines = [i for i, ch in enumerate(text) if ch == "\n"]
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_ans_style.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	assert "ANS() call after END_PGML" in issues[0]["message"]


#============================================

def test_run_no_warning_when_pure_pgml_style() -> None:
	text = """DOCUMENT();
loadMacros("PGML.pl");

$answer = Real(42);

BEGIN_PGML
What is 6 times 7?

[_]{$answer}
END_PGML

ENDDOCUMENT();
"""
	newlines = [i for i, ch in enumerate(text) if ch == "\n"]
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_ans_style.run(context)
	assert issues == []


#============================================

def test_run_no_warning_when_no_pgml_block() -> None:
	text = """DOCUMENT();
loadMacros("PGstandard.pl");

$answer = Real(42);

BEGIN_TEXT
What is 6 times 7?
\\{ans_rule(10)\\}
END_TEXT

ANS($answer->cmp());

ENDDOCUMENT();
"""
	newlines = [i for i, ch in enumerate(text) if ch == "\n"]
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_ans_style.run(context)
	assert issues == []


#============================================

def test_run_multiple_ans_calls_after_pgml() -> None:
	text = """DOCUMENT();
loadMacros("PGML.pl");

$ans1 = Real(1);
$ans2 = Real(2);

BEGIN_PGML
Question here.
END_PGML

ANS($ans1->cmp());
ANS($ans2->cmp());

ENDDOCUMENT();
"""
	newlines = [i for i, ch in enumerate(text) if ch == "\n"]
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_ans_style.run(context)
	assert len(issues) == 2
	assert all(issue["severity"] == "WARNING" for issue in issues)


#============================================

def test_run_with_radiobuttons_mixed_style() -> None:
	text = """DOCUMENT();
loadMacros("PGML.pl", "parserRadioButtons.pl");

$rb = RadioButtons(["A", "B"], "A");

BEGIN_PGML
[@ $rb->buttons() @]*
END_PGML

ANS($rb->cmp());

ENDDOCUMENT();
"""
	newlines = [i for i, ch in enumerate(text) if ch == "\n"]
	context = {"text": text, "newlines": newlines}
	issues = pgml_lint.plugins.pgml_ans_style.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
