# Local modules
import pgml_lint.plugins.block_rules


#============================================

def test_run_warns_when_only_one_side_present() -> None:
	context = {
		"stripped_text": "START_FOO\n",
		"block_rules": [
			{
				"label": "FOO",
				"start_pattern": "START_FOO",
				"end_pattern": "END_FOO",
			},
		],
	}
	issues = pgml_lint.plugins.block_rules.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"


#============================================

def test_run_errors_when_counts_mismatch() -> None:
	context = {
		"stripped_text": "START_FOO\nSTART_FOO\nEND_FOO\n",
		"block_rules": [
			{
				"label": "FOO",
				"start_pattern": "START_FOO",
				"end_pattern": "END_FOO",
			},
		],
	}
	issues = pgml_lint.plugins.block_rules.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "ERROR"
