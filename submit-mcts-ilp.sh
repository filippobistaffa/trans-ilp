#!/bin/bash

BEEGFS="/mnt/beegfs/iiia/filippo.bistaffa"
ROOT_DIR="/home/filippo.bistaffa/mcts-ilp-rs"
EXECUTABLE="$ROOT_DIR/mcts-ilp.sh"
LOG_DIR="$BEEGFS/pmf/mcts-rw"
DATA_DIR="$ROOT_DIR/data"
POOL_DIR="$DATA_DIR/pmf_50"

mkdir -p $LOG_DIR
STDOUT=$LOG_DIR/$1-$2.stdout
STDERR=$LOG_DIR/$1-$2.stderr

tmpfile=$(mktemp)
sbatch 1> $tmpfile <<EOF
#!/bin/bash
#SBATCH --job-name=mcts-$1-$2
#SBATCH --partition=quick
#SBATCH --time=5:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=/dev/null
#SBATCH --error=/dev/null
spack load python@3.8.6%gcc@10.2.0
spack load py-numpy
echo $EXECUTABLE --shuffle --seed $2 $POOL_DIR/$1.csv 1> $STDOUT
srun $EXECUTABLE --shuffle --seed $2 $POOL_DIR/$1.csv 1>> $STDOUT 2>> $STDERR
RET=\$?
exit \$RET
EOF
