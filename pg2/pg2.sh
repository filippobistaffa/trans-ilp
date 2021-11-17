#!/bin/bash

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}
distance_matrix="$exec_dir/../data/gmaps_distance.csv"
time_matrix="$exec_dir/../data/gmaps_time.csv"
generation_time_budget=55
determinism_rate=0.62
candidate_list_length=6
seed=$RANDOM
env_k=0.5
threads=1

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        --generation)
            shift
            generation_time_budget="$1"
            shift
        ;;
        --seed)
            shift
            seed="$1"
            shift
        ;;
        *)
            instance="$1"
            shift
        ;;
    esac
done

if test "${instance}" && file ${instance} | grep -qE "CSV text|ASCII text"
then
    ${exec_dir}/pg2 ${instance} ${distance_matrix} ${time_matrix} ${seed} ${generation_time_budget} ${determinism_rate} ${candidate_list_length} ${threads} ${env_k}
else
    echo "Instance CSV file not found!" >&2
    exit 1
fi
