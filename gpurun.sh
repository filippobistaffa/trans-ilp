#!/bin/bash

n=50
start=0
end=199
seeds=50
tb=60
tau=8

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
        --seeds)
            shift
            seeds="$1"
            shift
        ;;
        -b|--budget)
            shift
            tb="$1"
            shift
        ;;
        -t|--tau)
            shift
            tau="$1"
            shift
        ;;
        *)
            args="$args$key "
            shift
        ;;
    esac
done

HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-rs-actor"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$HOME/log/pmf/$n-trans-actor-$tb-$tau"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$n"
mkdir -p $LOG_DIR

for i in $( seq $start $end )
do
    for s in $( seq 0 $(( $seeds - 1 )) )
    do
        gpurun $EXECUTABLE $POOL_DIR/$i.csv --seed $s --budget $tb --tau $tau $args 1> $LOG_DIR/$i-$s.stdout 2> $LOG_DIR/$i-$s.stderr
    done
done
