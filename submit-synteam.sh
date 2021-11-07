#!/bin/bash

LAMBDA=${3:-0.8}

if hash condor_submit 2>/dev/null
then

HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-tf"
EXEC_DIR="$ROOT_DIR/synteam"
EXECUTABLE="$EXEC_DIR/synteam.sh"
LOG_DIR="$HOME/log/tf/$1-synteam"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$2-$LAMBDA.stdout
STDLOG=$LOG_DIR/$2-$LAMBDA.stdlog
STDERR=$LOG_DIR/$2-$LAMBDA.stderr

tmpfile=$(mktemp)
condor_submit 1> $tmpfile <<EOF
universe = vanilla
stream_output = True
stream_error = True
initialdir = $EXEC_DIR
executable = $EXECUTABLE
arguments = $1 $2 $LAMBDA
log = $STDLOG
output = $STDOUT
error = $STDERR
queue
EOF

elif hash sbatch 2>/dev/null
then

HOME="/home/filippo.bistaffa"
ROOT_DIR="$HOME/trans-ilp-tf"
EXEC_DIR="$ROOT_DIR/synteam"
EXECUTABLE="./synteam.sh"
BEEGFS="$HOME/beegfs"
LOG_DIR="$BEEGFS/tf/$1-synteam"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$2-$LAMBDA.stdout
STDERR=$LOG_DIR/$2-$LAMBDA.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=synteam-$1-$2-$LAMBDA
#SBATCH --partition=general-new
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --chdir=$EXEC_DIR
srun $EXECUTABLE $1 $2 $LAMBDA 1> $STDOUT 2> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
