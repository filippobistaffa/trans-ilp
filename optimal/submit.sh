#!/bin/bash

i=1
n=50
t="../data/task_english"
lambda=0.8

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
        -t|--task)
            shift
            t="$1"
            shift
        ;;
        -l|--lambda)
            shift
            lambda="$1"
            shift
        ;;
    esac
done

if hash condor_submit 2>/dev/null
then

HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-tf"
EXECUTABLE="$ROOT_DIR/optimal/optimal"
LOG_DIR="$HOME/log/tf/$n-$lambda-optimal"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pools_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i.stdout
STDERR=$LOG_DIR/$i.stderr
STDLOG=$LOG_DIR/$i.stdlog

tmpfile=$(mktemp)
condor_submit 1> $tmpfile <<EOF
universe = vanilla
stream_output = True
stream_error = True
executable = $EXECUTABLE
arguments = -i $POOL_DIR/$i.json -t $(readlink -f $t) -l $lambda
log = $STDLOG
output = $STDOUT
error = $STDERR
queue
EOF

elif hash sbatch 2>/dev/null
then

BEEGFS="/mnt/beegfs/iiia/filippo.bistaffa"
ROOT_DIR="/home/filippo.bistaffa/trans-ilp-tf"
EXECUTABLE="$ROOT_DIR/optimal/optimal"
LOG_DIR="$BEEGFS/tf/$n-$lambda-optimal"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pools_$n"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$i.stdout
STDERR=$LOG_DIR/$i.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=optimal-$n-$i
#SBATCH --partition=general-new
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
echo $EXECUTABLE -i $POOL_DIR/$i.json -t $(readlink -f $t) -l $lambda 1> $STDOUT
srun $EXECUTABLE -i $POOL_DIR/$i.json -t $(readlink -f $t) -l $lambda 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
