#!/bin/bash

i=1
n=50
tb=60
seed=$RANDOM
lambda=0.8
args=""

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        -i)
            shift
            i="$1"
            shift
        ;;
        -n)
            shift
            n="$1"
            shift
        ;;
        -b|--budget)
            shift
            tb="$1"
            shift
        ;;
        -s|--seed)
            shift
            seed="$1"
            shift
        ;;
        -l|--lambda)
            shift
            lambda="$1"
            shift
        ;;
        *)
            args="$args$key "
            shift
        ;;
    esac
done

if hash condor_submit 2>/dev/null
then

HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-tf"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$HOME/log/tf/$n-$lambda-trans-$tb"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pools_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i-$seed.stdout
STDERR=$LOG_DIR/$i-$seed.stderr
STDLOG=$LOG_DIR/$i-$seed.stdlog

tmpfile=$(mktemp)
condor_submit 1> $tmpfile <<EOF
universe = vanilla
stream_output = True
stream_error = True
executable = $EXECUTABLE
arguments = $POOL_DIR/$i.json --seed $seed --budget $tb --lambda $lambda $args
log = $STDLOG
output = $STDOUT
error = $STDERR
getenv = true
request_gpus = 1
queue
EOF

elif hash sbatch 2>/dev/null
then

HOME="/home/filippo.bistaffa"
BEEGFS="$HOME/beegfs"
ROOT_DIR="$HOME/trans-ilp-tf"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$BEEGFS/tf/$n-$lambda-trans-$tb"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pools_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i-$seed.stdout
STDERR=$LOG_DIR/$i-$seed.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=trans-$n-$i-$tb
#SBATCH --partition=quick
#SBATCH --time=5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
spack load --first python@3.8.6%gcc@10.2.0
spack load --first py-torch
echo $EXECUTABLE $POOL_DIR/$i.json --seed $seed --budget $tb --lambda $lambda $args 1> $STDOUT
srun $EXECUTABLE $POOL_DIR/$i.json --seed $seed --budget $tb --lambda $lambda $args 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
