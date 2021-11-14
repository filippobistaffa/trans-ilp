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
    args = parser.parse_args()

    all_idxs = list(range(data.pool_size()))
    file_idx = 0
    #print('coals_{:04d}.csv'.format(file_idx))
    out_file = open('coals/coals_{:04d}.csv'.format(file_idx), 'w')

    for idx, coal in enumerate(combinations(all_idxs, args.max_size)):
        out_file.write(','.join([str(i) for i in coal]))
        out_file.write('\n')
        if (idx and idx % (500 * 3600) == 0):
            out_file.close()
            file_idx += 1
            #print('coals_{:04d}.csv'.format(file_idx))
            out_file = open('coals/coals_{:04d}.csv'.format(file_idx), 'w')
    out_file.close()