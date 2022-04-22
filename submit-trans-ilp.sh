#!/bin/bash

i=0
n=50
tb=60
seed=$RANDOM
tau=8
priority=0
gpu=false
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
        -t|--tau)
            shift
            tau="$1"
            shift
        ;;
        -p|--priority)
            shift
            priority="$1"
            shift
        ;;
        --gpu)
            shift
            gpu=true
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
ROOT_DIR="$HOME/trans-ilp-rs"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$HOME/log/pmf/$n-trans-actor-$tb-$tau"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$n"

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
arguments = $POOL_DIR/$i.csv --seed $seed --budget $tb --tau $tau $args
log = $STDLOG
output = $STDOUT
error = $STDERR
getenv = true
priority = $priority
request_gpus = 1
queue
EOF

elif hash sbatch 2>/dev/null
then

HOME="/home/filippo.bistaffa"
BEEGFS="$HOME/beegfs"
ROOT_DIR="$HOME/trans-ilp-rs"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$BEEGFS/pmf/$n-trans-actor-$tb-$tau"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$n"

if [ "$gpu" = true ]
then
    partition="gpu"
    spackcuda="spack load cuda@11.4.1"
    gres="#SBATCH --gres=gpu:1"
    LOG_DIR="${LOG_DIR}-gpu"
else
    partition="quick"
    spackcuda=""
    gres=""
fi

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i-$seed.stdout
STDERR=$LOG_DIR/$i-$seed.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=trans-$n-$i-$seed-$tb
#SBATCH --partition=$partition
$gres
#SBATCH --time=5:30
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
spack load --first gcc@10.2.0
spack load --first py-numpy@1.21.2
$spackcuda
echo $EXECUTABLE $POOL_DIR/$i.csv --seed $seed --budget $tb --tau $tau $args 1> $STDOUT
srun $EXECUTABLE $POOL_DIR/$i.csv --seed $seed --budget $tb --tau $tau $args 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
