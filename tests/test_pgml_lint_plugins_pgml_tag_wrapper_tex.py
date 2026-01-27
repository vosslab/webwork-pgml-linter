# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_tag_wrapper_tex


#============================================

def test_tex_payload_warns() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[<div>]{ [ 'div' ] }{ [ '\\\\parbox{0.55\\\\linewidth}{', '}' ] }
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_tag_wrapper_tex.run(context)
	assert any("TeX payload" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_empty_tex_payload_ok() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[<div>]{ [ 'div' ] }{ }
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_tag_wrapper_tex.run(context)
	assert issues == []


#============================================

def test_no_tex_payload_ok() -> None:
	text = """DOCUMENT();
BEGIN_PGML
[<div>]{['div']}
END_PGML
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_tag_wrapper_tex.run(context)
	assert issues == []
