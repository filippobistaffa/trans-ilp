#!/bin/bash

n=50
start=1
end=2
seeds=5

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        -n)
            shift
            n="$1"
            shift
        ;;
        --start)
            shift
            start="$1"
            shift
        ;;
        --end)
            shift
            end="$1"
            shift
        ;;
        *)
            args="$args$key "
            shift
        ;;
    esac
done

for i in $( seq $start $end )
do
    for s in $( seq 0 $(( $seeds - 1 )) )
    do
        ./submit-trans-ilp.sh -n $n -i $i -s $s $args
    done
done
