#!/bin/bash

if [ $( hostname ) == "mlui01.ific.uv.es" ]
then

ENTROPY="0.05"
HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-rs"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$HOME/log/pmf/$1-trans-$ENTROPY-ilp"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$1"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$2.stdout
STDERR=$LOG_DIR/$2.stderr
STDLOG=$LOG_DIR/$2.stdlog

tmpfile=$(mktemp)
condor_submit 1> $tmpfile <<EOF
universe = vanilla
stream_output = True
stream_error = True
executable = $EXECUTABLE
arguments = $POOL_DIR/$2.csv
log = $STDLOG
output = $STDOUT
error = $STDERR
request_gpus = 1
queue
EOF

elif [ $( hostname ) == "vega.iiia.csic.es" ]
then

ENTROPY="0.05"
HOME="/home/filippo.bistaffa"
BEEGFS="$HOME/beegfs"
ROOT_DIR="$HOME/mcts-ilp-rs"
EXECUTABLE="$ROOT_DIR/trans-ilp.sh"
LOG_DIR="$BEEGFS/pmf/$1-trans-$ENTROPY-ilp"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$1"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$2.stdout
STDERR=$LOG_DIR/$2.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=trans-$1-$2
#SBATCH --partition=quick
#SBATCH --time=5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
spack load --first python@3.8.6%gcc@10.2.0
spack load --first py-torch
echo $EXECUTABLE --seed $RANDOM $POOL_DIR/$2.csv 1> $STDOUT
srun $EXECUTABLE --seed $RANDOM $POOL_DIR/$2.csv 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown host"
fi
