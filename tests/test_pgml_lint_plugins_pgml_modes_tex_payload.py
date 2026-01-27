# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_modes_tex_payload


#============================================

def test_modes_tex_payload_warns_on_non_empty_string() -> None:
	text = """DOCUMENT();
$choice_carbohydrates = MODES(
	TeX => "Carbohydrates (monosaccharides)",
	HTML => "<span>Carbohydrates</span>",
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_tex_payload.run(context)
	assert any("TeX payload is non-empty" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_modes_tex_payload_allows_empty_string() -> None:
	text = """DOCUMENT();
$choice_carbohydrates = MODES(
	TeX => "",
	HTML => "<span>Carbohydrates</span>",
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_tex_payload.run(context)
	assert issues == []


#============================================

def test_modes_tex_payload_allows_empty_q_string() -> None:
	text = """DOCUMENT();
$choice_carbohydrates = MODES(
	TeX => q{},
	HTML => "<span>Carbohydrates</span>",
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_tex_payload.run(context)
	assert issues == []


#============================================

def test_modes_tex_payload_warns_on_variable() -> None:
	text = """DOCUMENT();
$choice_carbohydrates = MODES(
	TeX => $label,
	HTML => "<span>Carbohydrates</span>",
);
ENDDOCUMENT();
"""
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_modes_tex_payload.run(context)
	assert any("TeX payload is non-empty" in str(issue.get("message", "")) for issue in issues)
