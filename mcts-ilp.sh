#!/bin/bash

# total time budget in seconds
time_budget=60

# number of candidates to print
best=30

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}

candidates=$(mktemp)
start=$(date +%s)
python3 $exec_dir/mcts.py $* > $candidates
end=$(date +%s)
runtime=$((end-start))
echo "Computed $(wc -l < $candidates) candidates in $runtime seconds"
echo "Best $best candidates:"
cat $candidates | LC_ALL=C sort -r -gk1,1 -t, | head -n $best
ilp_tb=$((time_budget-runtime))
$exec_dir/ilp/ilp $candidates $ilp_tb
rm $candidates