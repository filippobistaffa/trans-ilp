#!/bin/bash

# total time budget in seconds
time_budget=60

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}

candidates=$(mktemp)
start=`date +%s`
$exec_dir/pg2/pg2.sh $* > $candidates
end=`date +%s`
runtime=$((end-start))
ilp_tb=$((time_budget-runtime))
$exec_dir/ilp/ilp $candidates $ilp_tb
#cat $candidates | sort -gk1,1 -t, | tail -n 30
rm $candidates
