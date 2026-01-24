#!/bin/bash
# Extract files with issues from test results

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
OUTPUT_FILE="${OUTPUT_DIR}/files_with_issues.txt"

mkdir -p "$OUTPUT_DIR"

grep "issue(s)" test_results_2000.txt | \
    grep -v "^Total files" | \
    sed 's/\[.*\] Testing //' | \
    sed 's/\.\.\. [0-9]* issue.*//' | \
    awk '{print "OTHER_REPOS-do_not_commit/webwork-pgml-opl-training-set/" $0}' > "$OUTPUT_FILE"

echo "Extracted $(wc -l < "$OUTPUT_FILE") files with issues"
head -10 "$OUTPUT_FILE"
