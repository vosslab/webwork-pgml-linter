# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_seed_variation


#============================================

def test_no_variation_warns() -> None:
	text = "DOCUMENT();\nContext('Numeric');\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_variation.run(context)
	assert any("seed-based randomization" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_random_suppresses_warning() -> None:
	text = "DOCUMENT();\n$a = random(1, 5, 1);\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_variation.run(context)
	assert issues == []


#============================================

def test_problem_seed_suppresses_warning() -> None:
	text = "DOCUMENT();\n$seed = $problemSeed;\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_variation.run(context)
	assert issues == []


#============================================

def test_nchoosek_suppresses_warning() -> None:
	text = "DOCUMENT();\n@pick = NchooseK(10, 3);\nENDDOCUMENT();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_seed_variation.run(context)
	assert issues == []
