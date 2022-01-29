#!/bin/bash

i=0
n=50
tb=60
seed=$RANDOM
priority=0
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
ROOT_DIR="$HOME/trans-ilp-rs"
EXECUTABLE="$ROOT_DIR/pg2-ilp.sh"
LOG_DIR="$HOME/log/pmf/$n-pg2-$tb"
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
arguments = $POOL_DIR/$i.csv --seed $seed --budget $tb $args
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
ROOT_DIR="/home/filippo.bistaffa/trans-ilp-rs"
EXECUTABLE="$ROOT_DIR/pg2-ilp.sh"
LOG_DIR="$BEEGFS/pmf/$n-pg2-$tb"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i-$seed.stdout
STDERR=$LOG_DIR/$i-$seed.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=pg2-$n-$i-$tb
#SBATCH --partition=quick
#SBATCH --time=10:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
echo $EXECUTABLE $POOL_DIR/$i.csv --seed $seed --budget $tb $args 1> $STDOUT
srun $EXECUTABLE $POOL_DIR/$i.csv --seed $seed --budget $tb $args 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
