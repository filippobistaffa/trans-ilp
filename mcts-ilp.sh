#!/bin/bash

# total time budget in seconds
time_budget=60

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}

candidates=$(mktemp)
start=`date +%s`
python3 $exec_dir/mcts.py $* > $candidates
end=`date +%s`
runtime=$((end-start))
ilp_tb=$((time_budget-runtime))
$exec_dir/ilp/ilp $candidates $ilp_tb
rm $candidates
