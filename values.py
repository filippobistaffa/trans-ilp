from oracle.oracle import oracle
from oracle.oracle import OracleData
import argparse as ap
import numpy as np
import os

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', type=str, help='Pool JSON file')
    parser.add_argument('input', type=str, help='Input CSV file')
    parser.add_argument('output', type=str, help='Output CSV file')
    parser.add_argument('--task', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'task_english'), help='Task input file')
    args = parser.parse_args()

    # read input data
    data = OracleData(args.pool, args.task)
    coals = np.genfromtxt(args.input, delimiter=',', dtype=np.uint32)

    with open(args.output, 'w') as out_file:
        for idx in range(coals.shape[0]):
            coal = coals[idx]
            value = oracle(coal, data)
            out_file.write('{},{}'.format(value, ','.join([str(i) for i in coal])))
            out_file.write('\n')
