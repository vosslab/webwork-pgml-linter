# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_label_dot


#============================================

def test_run_warns_on_chr_dot_label() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $label = chr(65 + $i) . '. ';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_label_dot.run(context)
	assert len(issues) == 1
	assert issues[0]["severity"] == "WARNING"


#============================================

def test_run_allows_bold_label() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

my $label = '*' . $ALPHABET[$i] . '.* ';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_label_dot.run(context)
	assert len(issues) == 0
