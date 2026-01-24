# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_solution_hint_macros


#============================================

def test_run_warns_on_solution_macro() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

SOLUTION(EV3(<<'END_SOLUTION'));
This is the solution.
END_SOLUTION

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "SOLUTION()" in message
	assert "deprecated" in message.lower()
	assert "BEGIN_PGML_SOLUTION" in message


#============================================

def test_run_warns_on_hint_macro() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

HINT(EV3(<<'END_HINT'));
This is a hint.
END_HINT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	message = str(issues[0].get("message", ""))
	assert "HINT()" in message
	assert "deprecated" in message.lower()
	assert "BEGIN_PGML_HINT" in message


#============================================

def test_run_no_warning_with_pgml_blocks() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

BEGIN_PGML
Problem text.
END_PGML

BEGIN_PGML_SOLUTION
This is the solution using modern PGML.
END_PGML_SOLUTION

BEGIN_PGML_HINT
This is a hint using modern PGML.
END_PGML_HINT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 0


#============================================

def test_run_detects_both_solution_and_hint() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

SOLUTION(EV3(<<'END_SOLUTION'));
Solution here.
END_SOLUTION

HINT(EV3(<<'END_HINT'));
Hint here.
END_HINT

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 2
	messages = [str(issue.get("message", "")) for issue in issues]
	assert any("SOLUTION()" in msg for msg in messages)
	assert any("HINT()" in msg for msg in messages)


#============================================

def test_run_case_insensitive() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

Solution(EV3(<<'END'));
Lowercase solution.
END

Hint(EV3(<<'END'));
Lowercase hint.
END

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 2


#============================================

def test_run_multiple_solutions() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl');

SOLUTION(EV3(<<'END_SOLUTION'));
First solution.
END_SOLUTION

SOLUTION(EV3(<<'END_SOLUTION'));
Second solution.
END_SOLUTION

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_solution_hint_macros.run(context)
	assert len(issues) == 2
