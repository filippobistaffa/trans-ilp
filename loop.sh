#!/bin/bash

trans=false
pg2=true

n=50
start=0
total=2000

if [[ $( hostname ) =~ ^mlui0(1|2)\.ific\.uv\.es$ ]]
then
    step=$total
    delay=0
elif [ $( hostname ) == "vega.iiia.csic.es" ]
then
    step=200
    delay=600
else
    echo "Unknown host"
    exit
fi

i=$start

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
