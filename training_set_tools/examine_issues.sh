#!/bin/bash
# Examine each file with issues from the 1000-file test

FILES=(
"problems/Contrib/RRCC/College_Algebra/MAT121/6.2/CCD_CCCS_Openstax_AlgTrig_AT-1-001-AS_6_2_27.pg"
"problems/Contrib/PCC/CollegeAlgebra/FunctionComposition/DifferenceQuotient60.pg"
"problems/Contrib/CCCS/AlgebraicLiteracy/Solving_Equations/Power_Function_1.pg"
"problems/Contrib/CUNY/CityTech/Precalculus/setExponential_Functions-Graphs/choice-graphs.pg"
"problems/OpenProblemLibrary/PCC/BasicAlgebra/PointSlopeForm/ParallelPerpendicular170.pg"
)

BASE="OTHER_REPOS-do_not_commit/webwork-pgml-opl-training-set"

for file in "${FILES[@]}"; do
    echo "=== $file ==="
    /opt/homebrew/opt/python@3.12/bin/python3.12 ./tools/webwork_pgml_simple_lint.py -i "$BASE/$file" -v
    echo ""
done
