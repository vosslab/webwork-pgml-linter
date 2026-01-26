# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_header_tags


#============================================

def test_warns_on_noisy_header_tags() -> None:
	text = """## DESCRIPTION
## Test problem.
## ENDDESCRIPTION
## KEYWORDS('test','pgml','header')
## DBsubject('WeBWorK')
## DBchapter([REFER TO https://github.com/openwebwork/webwork-open-problem-library/blob/master/OpenProblemLibrary/Taxonomy])
## DBsection('')

DOCUMENT();
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_header_tags.run(context)
	assert len(issues) >= 3
	assert any("DBsubject" in str(issue.get("message", "")) for issue in issues)
	assert any("DBchapter" in str(issue.get("message", "")) for issue in issues)
	assert any("DBsection" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_warns_on_missing_header_tags() -> None:
	text = """## DESCRIPTION
## Only description.
## ENDDESCRIPTION

DOCUMENT();
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_header_tags.run(context)
	assert len(issues) >= 4
	assert any("Missing DBsubject" in str(issue.get("message", "")) for issue in issues)
	assert any("Missing DBchapter" in str(issue.get("message", "")) for issue in issues)
	assert any("Missing DBsection" in str(issue.get("message", "")) for issue in issues)
	assert any("Missing KEYWORDS" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_warns_on_description_missing_end() -> None:
	text = """## DESCRIPTION
## Missing end.
## KEYWORDS('one','two','three')

DOCUMENT();
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_header_tags.run(context)
	assert any("ENDDESCRIPTION" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_warns_on_keywords_rules() -> None:
	text = """## DESCRIPTION
## Test problem.
## ENDDESCRIPTION
## KEYWORDS('alpha','beta','alpha')
## DBsubject('Algebra')
## DBchapter('Linear')
## DBsection('Forms')

DOCUMENT();
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_header_tags.run(context)
	assert any("KEYWORDS contains duplicates" in str(issue.get("message", "")) for issue in issues)
