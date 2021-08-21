#!/bin/bash

exec_dir=$(readlink -f $0)
exec_dir=${exec_dir%/*}

distance_matrix="$exec_dir/../data/gmaps_distance.csv"
time_matrix="$exec_dir/../data/gmaps_time.csv"
time_budget=60
generation_portion=0.66666666
determinism_rate=0.62
candidate_list_length=6
seed=$RANDOM
env_k=0.5
threads=1

if [ $# -eq 2 ]
then
        seed=$2
fi

$exec_dir/pg2 $1 ${distance_matrix} ${time_matrix} ${seed} ${time_budget} ${generation_portion} ${determinism_rate} ${candidate_list_length} ${threads} ${env_k}
