# Local modules
import pgml_lint.plugins.pgml_blank_assignments


#============================================

def test_run_warns_on_unassigned_blank_vars() -> None:
	context = {"pgml_blank_vars": {"ans"}, "assigned_vars": set()}
	issues = pgml_lint.plugins.pgml_blank_assignments.run(context)
	assert len(issues) == 1
	assert "$ans" in issues[0]["message"]
