# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_seed_stability


#============================================

def test_rand_warns() -> None:
	text = "DOCUMENT();\n$a = rand(10);\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_stability.run(context)
	assert any("rand()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_method_rand_ignored() -> None:
	text = "DOCUMENT();\n$a = $PG_random_generator->rand(10);\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_stability.run(context)
	assert issues == []


#============================================

def test_time_warns() -> None:
	text = "DOCUMENT();\n$now = time();\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_stability.run(context)
	assert any("time()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_srand_warns() -> None:
	text = "DOCUMENT();\nSRAND(1234);\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_stability.run(context)
	assert any("SRAND" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_problem_randomize_warns() -> None:
	text = "DOCUMENT();\nProblemRandomize();\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_stability.run(context)
	assert any("ProblemRandomize" in str(issue.get("message", "")) for issue in issues)
