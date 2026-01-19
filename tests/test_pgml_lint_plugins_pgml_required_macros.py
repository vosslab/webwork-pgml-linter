# Local modules
import pgml_lint.plugins.pgml_required_macros


#============================================

def test_run_warns_when_pgml_macros_missing() -> None:
	context = {"uses_pgml": True, "macros_loaded": set()}
	issues = pgml_lint.plugins.pgml_required_macros.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"


#============================================

def test_run_no_warning_when_macro_present() -> None:
	context = {"uses_pgml": True, "macros_loaded": {"pgml.pl"}}
	issues = pgml_lint.plugins.pgml_required_macros.run(context)
	assert issues == []


#============================================

def test_run_no_warning_when_pgml_not_used() -> None:
	context = {"uses_pgml": False, "macros_loaded": set()}
	issues = pgml_lint.plugins.pgml_required_macros.run(context)
	assert issues == []
