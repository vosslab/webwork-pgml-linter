# Local modules
import pgml_lint.engine
import pgml_lint.plugins.pgml_function_signatures


#============================================

def test_random_arg_count_error() -> None:
	text = "my $x = random(1, 10);\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert any(issue["severity"] == "ERROR" for issue in issues)
	assert any("random()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_nchoosek_empty_args() -> None:
	text = "my @pick = NchooseK();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert any("NchooseK()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_dropdown_min_args_warning() -> None:
	text = "my $dd = DropDown(['A','B']);\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert any(issue["severity"] == "WARNING" for issue in issues)
	assert any("DropDown()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_typo_detection() -> None:
	text = "my $x = Dropdown(['A','B'], 1);\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert any("looks wrong" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_string_ignored() -> None:
	text = "my $x = \"random(1,2)\";\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert len(issues) == 0


#============================================

def test_oneof_min_args_warning() -> None:
	text = "my $x = OneOf();\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert any("OneOf()" in str(issue.get("message", "")) for issue in issues)


#============================================

def test_passthrough_args_skip_warning() -> None:
	text = "sub make_popup { return defined &DropDown ? DropDown(@_) : PopUp(@_); }\n"
	context = pgml_lint.engine.build_context(text, None, [], [])
	issues = pgml_lint.plugins.pgml_function_signatures.run(context)
	assert issues == []
