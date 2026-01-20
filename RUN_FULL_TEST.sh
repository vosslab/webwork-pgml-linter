#!/bin/bash
# Run the linter on all 9,386 PGML files and categorize results

echo "================================"
echo "PGML Linter - Full Test Run"
echo "================================"
echo ""
echo "This will:"
echo "  1. Lint all 9,386 PGML files"
echo "  2. Categorize issues into:"
echo "     - confirmed_bugs_pg.txt (real bugs)"
echo "     - mixed_legacy_pg.txt (old-style ANS)"
echo "     - likely_false_positives_pg.txt (parser limitations)"
echo ""
echo "Expected time: 5-10 minutes"
echo ""
read -p "Press Enter to start, or Ctrl+C to cancel..."

/opt/homebrew/opt/python@3.12/bin/python3.12 ./lint_and_categorize_all.py

echo ""
echo "Done! Check the output files for results."
