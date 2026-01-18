# PIP3 modules
import pytest

# local repo modules
import pgml_lint.parser


@pytest.mark.parametrize(
	"heredoc_opener",
	[
		"<<END_PGML",
		"<<-END_PGML",
		"<<'END_PGML'",
		"<<\"END_PGML\"",
	],
)
def test_strip_comments_preserves_hash_in_heredoc_body(heredoc_opener: str) -> None:
	text = (
		"$x = 1; # strip me\n"
		f"PGML::Format({heredoc_opener});\n"
		"Inside heredoc # keep me\n"
		"END_PGML\n"
		"$y = 2; # strip me too\n"
	)

	stripped = pgml_lint.parser.strip_comments(text)

	expected = (
		"$x = 1; \n"
		f"PGML::Format({heredoc_opener});\n"
		"Inside heredoc # keep me\n"
		"END_PGML\n"
		"$y = 2; \n"
	)

	assert stripped == expected


def test_strip_comments_preserves_hash_in_strings() -> None:
	text = (
		"$x = '# not a comment'; # comment\n"
		"$y = \"# not a comment\"; # comment\n"
	)
	stripped = pgml_lint.parser.strip_comments(text)
	assert stripped == "$x = '# not a comment'; \n$y = \"# not a comment\"; \n"


def test_iter_calls_supports_qualified_names() -> None:
	text = "PGML::Format(1, 2);\n"
	newlines = pgml_lint.parser.build_newline_index(text)
	calls = pgml_lint.parser.iter_calls(text, {"PGML::Format"}, newlines=newlines)
	assert len(calls) == 1
	assert calls[0]["name"] == "PGML::Format"
	assert calls[0]["arg_text"] == "1, 2"
	assert calls[0]["line"] == 1


def test_iter_calls_ignores_unbalanced_parens() -> None:
	text = "ANS($a->cmp(\n"
	newlines = pgml_lint.parser.build_newline_index(text)
	calls = pgml_lint.parser.iter_calls(text, {"ANS"}, newlines=newlines)
	assert calls == []
