#!/bin/bash

# default time budget in seconds
budget=60

# number of candidates to print
best=30

args=""

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        --budget)
            shift
            budget="$1"
            shift
        ;;
        *)
            args="$args$key "
            shift
        ;;
    esac
done

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}
candidates=$(mktemp)
start=$(date +%s)
python3 $exec_dir/trans.py $args > $candidates
ret=$?
if [ $ret -ne 0 ]
then
    exit
fi
end=$(date +%s)
runtime=$((end-start))
echo "Computed $(wc -l < $candidates) candidates in $runtime seconds"
echo "Best $best candidates:"
cat $candidates | LC_ALL=C sort -r -gk1,1 -t, | head -n $best
tilp=$((budget-runtime))
$exec_dir/ilp/ilp $candidates $tilp
rm $candidates
