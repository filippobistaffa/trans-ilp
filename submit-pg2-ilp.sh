#!/bin/bash

BEEGFS="/mnt/beegfs/iiia/filippo.bistaffa"
ROOT_DIR="/home/filippo.bistaffa/mcts-ilp-rs"
EXECUTABLE="$ROOT_DIR/pg2-ilp.sh"
LOG_DIR="$BEEGFS/pmf/$1-pg2"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_$1"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$2.stdout
STDERR=$LOG_DIR/$2.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=pg2-$1-$2
#SBATCH --partition=quick
#SBATCH --time=5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
echo $EXECUTABLE $POOL_DIR/$2.csv $RANDOM 1> $STDOUT
srun $EXECUTABLE $POOL_DIR/$2.csv $RANDOM 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF
