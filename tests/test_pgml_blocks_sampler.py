# Standard Library
from pathlib import Path

# Local modules
import pg_analyze.aggregate
import pg_analyze.main


def test_pgml_blocks_unknown_top_signatures_dump(tmp_path: Path) -> None:
	p = tmp_path / "a.pg"
	p.write_text(
		"BEGIN_PGML\n"
		"Answer: [_]{Real(3)->cmp()}\n"
		"END_PGML\n",
		encoding="utf-8",
	)

	agg = pg_analyze.aggregate.Aggregator(needs_review_limit=200, out_dir=str(tmp_path))
	try:
		agg.add_record({
			"file": str(p),
			"types": ["unknown_pgml_blank"],
			"confidence": 0.25,
			"pgml_blank_marker_count": 1,
			"pgml_payload_evaluator_count": 0,
			"has_named_ans_rule_token": 0,
			"has_ans_rule_token": 0,
			"has_named_popup_list_token": 0,
			"has_cmp_token": 0,
			"has_answer_ctor": 0,
			"has_ans_token": 0,
		})
		pg_analyze.main._write_pgml_blocks_unknown_top_signatures(str(tmp_path), agg)
	finally:
		agg.close()

	out = (tmp_path / "diagnostics" / "pgml_blocks_unknown_pgml_blank_top_signatures.txt").read_text(encoding="utf-8")
	assert f"file={p}" in out
	assert "signature=pgml_blank_no_grading_signals" in out
	assert "Answer: [_]{Real(3)->cmp()}" in out
