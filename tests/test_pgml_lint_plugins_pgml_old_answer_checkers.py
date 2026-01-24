# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_old_answer_checkers


#============================================

def test_run_warns_on_num_cmp() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
Enter answer: \\{ans_rule(20)\\}
END_TEXT

ANS(num_cmp($answer));

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "num_cmp" in message
	assert "deprecated" in message.lower()
	assert "->cmp()" in message


#============================================

def test_run_warns_on_str_cmp() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

ANS(str_cmp("answer"));

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 1
	assert "str_cmp" in str(issues[0].get("message", ""))


#============================================

def test_run_warns_on_fun_cmp() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

ANS(fun_cmp("x^2", var => 'x'));

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 1
	assert "fun_cmp" in str(issues[0].get("message", ""))


#============================================

def test_run_detects_std_variants() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

ANS(std_num_cmp($ans1));
ANS(std_str_cmp($ans2));
ANS(std_fun_cmp($ans3));

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 3


#============================================

def test_run_no_warning_with_mathobjects() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

$answer = Compute("42");

BEGIN_PGML
Answer: [_]{$answer}
END_PGML

# Or explicitly:
# ANS($answer->cmp());

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_multiple_old_checkers() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

ANS(num_cmp($ans1));
ANS(str_cmp($ans2));
ANS(num_cmp($ans3));

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_old_answer_checkers.run(context)
	assert len(issues) == 3
