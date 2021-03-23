#!/bin/bash

EXECUTABLE="python3 /home/filippo/iiia/mcts-rs/main.py"
DATA_DIR="/home/filippo/iiia/mcts-rs/data"

# Fixed parameters
DISTANCE="$DATA_DIR/gmaps_distance.csv"
TIME="$DATA_DIR/gmaps_time.csv"
ITERATIONS=1000

CANDIDATEID=$1
INSTANCEID=$2
SEED=$3
INSTANCE=$4

shift 4 || exit 1
CAND_PARAMS=$*

STDOUT="c${CANDIDATEID}-${INSTANCEID}.out"
STDERR="c${CANDIDATENUM}${INSTANCEID}.err"

# In case of error, we print the current time:
error() {
    echo "`TZ=UTC date`: error: $@" >&2
    exit 1
}

#if [ ! -x "${EXECUTABLE}" ]; then
#    error "${EXECUTABLE}: not found or not executable (pwd: $(pwd))"
#fi

# Call EXECUTABLE
echo $EXECUTABLE $INSTANCE --distance $DISTANCE --time $TIME --seed $SEED --iterations $ITERATIONS ${CAND_PARAMS} 1> $STDOUT
$EXECUTABLE $INSTANCE --distance $DISTANCE --time $TIME --seed $SEED --iterations $ITERATIONS ${CAND_PARAMS} 1>> $STDOUT 2>> $STDERR

if [[ ! -s "${STDOUT}" ]]
then
    error "${STDOUT}: No such file or directory"
fi

RW=$(cat ${STDOUT} | tail -n 1)
echo "$RW"

#rm -f "${STDOUT}" "${STDERR}"
exit 0
