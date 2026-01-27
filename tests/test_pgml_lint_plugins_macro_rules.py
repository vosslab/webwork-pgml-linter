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


#============================================

def test_run_warns_when_pg_version_too_low() -> None:
	rules = [
		{
			"label": "DropDown",
			"pattern": r"\bDropDown\s*\(",
			"min_pg_version": "2.18",
			"required_macros": ["parserPopUp.pl"],
		},
	]
	context = {
		"stripped_text": "DOCUMENT();\nDropDown([1,2], 1);\n",
		"macros_loaded": {"parserpopup.pl"},
		"macro_rules": rules,
		"pg_version": "2.17",
	}
	issues = pgml_lint.plugins.macro_rules.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"
	assert "requires pg 2.18" in issues[0]["message"].lower()


#============================================

def test_run_no_warning_when_pg_version_ok() -> None:
	rules = [
		{
			"label": "DropDown",
			"pattern": r"\bDropDown\s*\(",
			"min_pg_version": "2.18",
			"required_macros": ["parserPopUp.pl"],
		},
	]
	context = {
		"stripped_text": "DOCUMENT();\nDropDown([1,2], 1);\n",
		"macros_loaded": {"parserpopup.pl"},
		"macro_rules": rules,
		"pg_version": "2.19",
	}
	issues = pgml_lint.plugins.macro_rules.run(context)
	assert issues == []
