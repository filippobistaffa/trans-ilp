#!/bin/bash

trans=false
pg2=true

n=100
step=200
total=2000
delay=300

i=0
while true
do
    for j in $( seq 1 $step )
    do
        if [[ $i == $total ]]
        then
            exit
        fi
        if [ "$trans" = true ]
        then
            ./submit-trans-ilp.sh $n $i
        fi
        if [ "$pg2" = true ]
        then
            ./submit-pg2-ilp.sh $n $i
        fi
        i=$((i+1))
    done
    sleep $delay
done
