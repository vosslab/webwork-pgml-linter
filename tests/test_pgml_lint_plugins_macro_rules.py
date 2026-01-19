# Local modules
import pgml_lint.plugins.macro_rules


#============================================

def test_run_warns_when_required_macro_missing() -> None:
	rules = [
		{
			"label": "RadioButtons",
			"pattern": r"\bRadioButtons\s*\(",
			"required_macros": ["parserRadioButtons.pl"],
		},
	]
	context = {
		"stripped_text": "DOCUMENT();\nRadioButtons(1);\n",
		"macros_loaded": set(),
		"macro_rules": rules,
	}
	issues = pgml_lint.plugins.macro_rules.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	assert "radiobuttons" in issues[0]["message"].lower()


#============================================

def test_run_no_warning_when_macro_present() -> None:
	rules = [
		{
			"label": "RadioButtons",
			"pattern": r"\bRadioButtons\s*\(",
			"required_macros": ["parserRadioButtons.pl"],
		},
	]
	context = {
		"stripped_text": "DOCUMENT();\nRadioButtons(1);\n",
		"macros_loaded": {"parserradiobuttons.pl"},
		"macro_rules": rules,
	}
	issues = pgml_lint.plugins.macro_rules.run(context)
	assert issues == []
