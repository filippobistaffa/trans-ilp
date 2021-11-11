#!/bin/bash

n=50
start=0
end=2000
pg2=false
trans=false

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
        --trans)
            trans=true
            shift
        ;;
        --pg2)
            pg2=true
            shift
        ;;
        *)
            args="$args$key "
            shift
        ;;
    esac
done

if [ "$trans" = false ] && [ "$pg2" = false ]
then
    echo "--trans or --pg2 (or both) arguments are required"
    exit 1
fi

if hash condor_submit 2>/dev/null
then
    step=$end
    delay=0
elif hash sbatch 2>/dev/null
then
    step=200
    delay=600
else
    echo "Unknown cluster"
    exit 1
fi

i=$start

while true
do
    for j in $( seq 1 $step )
    do
        if [[ $i == $end ]]
        then
            exit
        fi
        if [ "$trans" = true ]
        then
            ./submit-trans-ilp.sh -n $n -i $i $args
        fi
        if [ "$pg2" = true ]
        then
            ./submit-pg2-ilp.sh -n $n -i $i $args
        fi
        i=$((i+1))
    done
    sleep $delay
done
