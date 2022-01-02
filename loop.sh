#!/bin/bash

function wait_empty_queue {
    while true
    do
        if hash condor_submit 2>/dev/null
        then
            remaining=$( condor_q | tail -n 3 | head -n 1 | cut -f 4 -d\  )
        elif hash sbatch 2>/dev/null
        then
            remaining=$( squeue -h | wc -l )
        else
            echo "Unknown cluster"
            exit 1
        fi
        #echo "$remaining jobs remaining" 
        if [[ $remaining == 0 ]]
        then
            return
        else
            #echo "Waiting queue to be empty..." 
            sleep 60
        fi
    done
}

n=50
start=0
end=199
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
        *)
            args="$args$key "
            shift
        ;;
    esac
done

j=0

for i in $( seq $start $end )
do
        if [[ $j == $step ]]
        then
            wait_empty_queue
            j=0
        fi
        ./submit.sh -n $n -i $i $args
        j=$((j+1))
done
