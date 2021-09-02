#!/bin/bash

EXEC_DIR="/home/filippo.bistaffa/mcts-ilp-tf/synteam"
EXECUTABLE="./synteam.sh"
BEEGFS="/mnt/beegfs/iiia/filippo.bistaffa"
LOG_DIR="$BEEGFS/tf/synteam"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$1-$2.stdout
STDERR=$LOG_DIR/$1-$2.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=synteam-$1-$2
#SBATCH --partition=general-new
#SBATCH --time=6:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
#SBATCH --chdir=$EXEC_DIR
srun $EXECUTABLE $1 $2 1> $STDOUT 2> $STDERR
RET=\$?
exit \$RET
EOF
