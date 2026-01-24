#!/usr/bin/env python3
"""
Test the improved parser on known false positive patterns.
"""

# local repo modules
from pgml_lint.parser import extract_assigned_vars

#============================================
def test_list_assignment():
	"""Test list assignment detection."""
	code = """
	($min, $Q1, $median, $Q3, $max) = five_point_summary(@data);
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'min', 'Q1', 'median', 'Q3', 'max'}
	assert expected <= vars_found, f"Missing vars: {expected - vars_found}"
	print("✓ List assignment: ($a, $b, $c) = func()")

#============================================
def test_array_element_assignment():
	"""Test array element assignment detection."""
	code = """
	foreach my $i (0..5) {
		$nFact[$i] = Real($n[$i]);
		$kFact[$i] = Real($k[$i]);
	}
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'nFact', 'kFact', 'i'}
	assert expected <= vars_found, f"Missing vars: {expected - vars_found}"
	print("✓ Array element assignment: $arr[0] = value")

#============================================
def test_hash_element_assignment():
	"""Test hash element assignment detection."""
	code = """
	$config{timeout} = 300;
	$config{max_tries} = 3;
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'config'}
	assert expected <= vars_found, f"Missing vars: {expected - vars_found}"
	print("✓ Hash element assignment: $hash{key} = value")

#============================================
def test_mixed_patterns():
	"""Test mixed patterns together."""
	code = """
	my $answer = 42;
	$popup = PopUp(['A', 'B'], 'A');
	($a, $b, $c) = (1, 2, 3);
	$arr[0] = Real(5);
	$hash{key} = "value";
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'answer', 'popup', 'a', 'b', 'c', 'arr', 'hash'}
	assert expected <= vars_found, f"Missing vars: {expected - vars_found}"
	print("✓ Mixed patterns work together")

#============================================
def test_real_world_stats():
	"""Test real-world statistics code."""
	code = """
	($min, $Q1, $median, $Q3, $max) = five_point_summary(@p);
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'min', 'Q1', 'median', 'Q3', 'max'}
	missing = expected - vars_found
	assert not missing, f"Missing stats vars: {missing}"
	print("✓ Statistics five_point_summary pattern")

#============================================
def test_real_world_loops():
	"""Test real-world loop patterns."""
	code = """
	foreach my $i (0..1) {
		$nFact[$i] = Real("$n[$i]!");
		$kFact[$i] = Real("$k[$i]!");
		$nkFact[$i] = Real("($n[$i]-$k[$i])!");
		$pascal[$i] = Real("$nFact[$i]/($kFact[$i]*$nkFact[$i])");
	}
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'i', 'nFact', 'kFact', 'nkFact', 'pascal'}
	missing = expected - vars_found
	assert not missing, f"Missing loop vars: {missing}"
	print("✓ Binomial theorem loop pattern")

#============================================
def test_real_world_series():
	"""Test real-world series patterns."""
	code = """
	foreach my $i (0..3) {
		$last[$i] = Real($init[$i]+$diff[$i]*($n[$i]-1));
		$pair[$i] = $seq[$i][0]+$last[$i];
		$sum[$i] = Real($pair[$i]*$n[$i]/2);
	}
	"""
	vars_found = extract_assigned_vars(code)
	expected = {'i', 'last', 'pair', 'sum'}
	missing = expected - vars_found
	assert not missing, f"Missing series vars: {missing}"
	print("✓ Arithmetic series loop pattern")

#============================================
def main():
	"""Run all tests."""
	print("Testing improved parser...")
	print()

	try:
		test_list_assignment()
		test_array_element_assignment()
		test_hash_element_assignment()
		test_mixed_patterns()
		test_real_world_stats()
		test_real_world_loops()
		test_real_world_series()

		print()
		print("="*70)
		print("All tests passed! ✓")
		print("="*70)
		print()
		print("The parser now correctly handles:")
		print("  • List assignments: ($a, $b) = func()")
		print("  • Array autovivification: $arr[0] = value")
		print("  • Hash autovivification: $hash{key} = value")
		print("  • Complex loop patterns")
		print()

	except AssertionError as e:
		print()
		print(f"✗ Test failed: {e}")
		return 1

	return 0

#============================================
if __name__ == '__main__':
	exit(main())
