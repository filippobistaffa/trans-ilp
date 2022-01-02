#!/bin/bash

i=1
n=50
tb=60
seed=$RANDOM
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
        -p|--priority)
            shift
            priority="$1"
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
ROOT_DIR="$HOME/mcts-tf"
LOG_DIR="$HOME/log/tf/$n-mcts-$tb"
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
executable = /usr/bin/python3
arguments = $ROOT_DIR/main.py $POOL_DIR/$i.json --budget $tb --seed $seed $args
log = $STDLOG
output = $STDOUT
error = $STDERR
getenv = true
priority = $priority
queue
EOF

elif hash sbatch 2>/dev/null
then

BEEGFS="/mnt/beegfs/iiia/filippo.bistaffa"
ROOT_DIR="$HOME/mcts-tf"
LOG_DIR="$BEEGFS/tf/$n-mcts-$tb"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pools_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i-$seed.stdout
STDERR=$LOG_DIR/$i-$seed.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=mcts-$n-$i-$seed
#SBATCH --partition=quick
#SBATCH --time=10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
spack load python@3.8.6%gcc@10.2.0
spack load --first py-numpy
echo python3 $ROOT_DIR/main.py $POOL_DIR/$i.json --budget $tb --seed $seed $args 1> $STDOUT
srun python3 $ROOT_DIR/main.py $POOL_DIR/$i.json --budget $tb --seed $seed $args 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
