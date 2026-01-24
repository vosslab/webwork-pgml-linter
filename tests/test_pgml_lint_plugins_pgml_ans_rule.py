# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_ans_rule


#============================================

def test_run_warns_on_ans_rule() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
Enter your answer: \\{ans_rule(20)\\}
END_TEXT

ANS($answer->cmp());

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_ans_rule.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "ans_rule" in message.lower()
	assert "deprecated" in message.lower()


#============================================

def test_run_no_warning_with_pgml_blanks() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Enter your answer: [_]{$answer}
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_ans_rule.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_multiple_ans_rule_calls() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
Answer 1: \\{ans_rule(10)\\}
Answer 2: \\{ans_rule(20)\\}
Answer 3: \\{ans_rule(30)\\}
END_TEXT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_ans_rule.run(context)
	assert len(issues) == 3


#============================================

def test_run_ignores_ans_rule_in_comments() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

# Old way: ans_rule(20)
# Don't use ans_rule anymore

BEGIN_PGML
Modern way: [_]{$answer}
END_PGML

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_ans_rule.run(context)
	# Comments are stripped in stripped_text, so no issues
	assert len(issues) == 0


#============================================

def test_run_detects_ans_rule_with_spaces() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

BEGIN_TEXT
With spaces: \\{ans_rule  (  15  )\\}
END_TEXT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_ans_rule.run(context)
	assert len(issues) == 1
