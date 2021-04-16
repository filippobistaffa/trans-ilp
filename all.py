from oracle.oracle import oracle
from oracle.oracle import OracleData
from itertools import combinations
import argparse as ap
import numpy as np
import os

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--max_size', type=int, default=5, help='Maximum coalition size (default = 5)')
    parser.add_argument('--task', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'task_english'), help='Task input file')
    args = parser.parse_args()

    # read input data
    data = OracleData(args.pool, args.task)
    all_idxs = list(range(data.pool_size()))
    coals = []

    for coal in combinations(all_idxs, args.max_size):
        coals.append(coal)
