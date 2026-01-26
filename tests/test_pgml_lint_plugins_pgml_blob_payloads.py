# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_blob_payloads


#============================================

def test_warns_on_base64_blob() -> None:
	long_blob = "A" * 900
	text = f"""DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

{long_blob}

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_blob_payloads.run(context)
	assert len(issues) >= 1


#============================================

def test_warns_on_base64_markers() -> None:
	text = """DOCUMENT();
loadMacros('PGstandard.pl', 'PGML.pl');

# ggbbase64 payload
ggbbase64 => 'abc';

somebase64 => 'abc';

ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_blob_payloads.run(context)
	assert len(issues) >= 2
