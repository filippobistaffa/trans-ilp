#!/bin/bash

k=5
n=50
lambda=0.8
priority=0

while [[ $# > 0 ]]
do
    key="$1"
    case $key in
        -n)
            shift
            n="$1"
            shift
        ;;
        -l|--lambda)
            shift
            lambda="$1"
            shift
        ;;
        -p|--priority)
            shift
            priority="$1"
            shift
        ;;
    esac
done

if hash condor_submit 2>/dev/null
then

HOME="/lhome/ext/iiia021/iiia0211"
ROOT_DIR="$HOME/trans-ilp-tf"
EXEC_DIR="$ROOT_DIR/synteam"
EXECUTABLE="$EXEC_DIR/synteam.sh"
LOG_DIR="$HOME/log/tf/$n-$lambda-synteam"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/all.stdout
STDLOG=$LOG_DIR/all.stdlog
STDERR=$LOG_DIR/all.stderr

tmpfile=$(mktemp)
condor_submit 1> $tmpfile <<EOF
universe = vanilla
stream_output = True
stream_error = True
initialdir = $EXEC_DIR
executable = $EXECUTABLE
arguments = $n $k $lambda
log = $STDLOG
output = $STDOUT
error = $STDERR
getenv = true
priority = $priority
queue
EOF

elif hash sbatch 2>/dev/null
then

HOME="/home/filippo.bistaffa"
ROOT_DIR="$HOME/trans-ilp-tf"
EXEC_DIR="$ROOT_DIR/synteam"
EXECUTABLE="./synteam.sh"
BEEGFS="$HOME/beegfs"
LOG_DIR="$BEEGFS/tf/$n-$lambda-synteam"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/all.stdout
STDERR=$LOG_DIR/all.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=synteam-$1-$2-$lambda
#SBATCH --partition=general-new
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --chdir=$EXEC_DIR
srun $EXECUTABLE $n $k $lambda 1> $STDOUT 2> $STDERR
RET=\$?
exit \$RET
EOF

else
echo "Unknown cluster"
fi
