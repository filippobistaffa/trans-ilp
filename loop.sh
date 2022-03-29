#!/bin/bash

function wait_empty_queue {
    while true
    do
        if hash condor_submit 2>/dev/null
        then
            remaining=$( condor_q | tail -n 3 | head -n 1 | cut -f 4 -d\  )
        elif hash sbatch 2>/dev/null
        then
            remaining=$( squeue --me -h | wc -l )
        else
            echo "Unknown cluster"
            exit 1
        fi
        echo "$remaining jobs remaining"
        if [[ $remaining == 0 ]]
        then
            return
        else
            echo "Waiting queue to be empty..."
            sleep 60
        fi
    done
}

n=50
start=0
end=199
seeds=50
pg2=false
trans=false
step=200

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

j=0

for i in $( seq $start $end )
do
    for s in $( seq 0 $(( $seeds - 1 )) )
    do
        if [[ $j == $step ]]
        then
            wait_empty_queue
            j=0
        fi
        if [ "$trans" = true ]
        then
            echo "Submitted Trans ($i $s)"
            ./submit-trans-ilp.sh -n $n -i $i -s $s $args
            j=$((j+1))
        fi
        if [[ $j == $step ]]
        then
            wait_empty_queue
            j=0
        fi
        if [ "$pg2" = true ]
        then
            echo "Submitted PG2 ($i $s)"
            ./submit-pg2-ilp.sh -n $n -i $i -s $s $args
            j=$((j+1))
        fi
    done
done
