import argparse as ap
import pandas as pd
import numpy as np
import bisect
import random
import os

n_z = 63
n_ts = 24 * 60 # minutes in a day

parser = ap.ArgumentParser()
parser.add_argument('--size', type=int, help='Pool size (default: 50)', default=50)
parser.add_argument('--step', type=int, help='Pool size (default: 720)', default=720)
parser.add_argument('--pools', type=int, help='Number of pools (default: 2000)', default=2000)
parser.add_argument('--dir', type=str, help='Output directory (default: pmf_50)', default="pmf_50")
parser.add_argument('--wait', type=int, help='Maximum waiting time (default: 5)', default=5)
args = parser.parse_args()

pmft_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pmf_2016-12_day_minute.gz")
pmft = pd.read_csv(pmft_file, delimiter = ",", usecols = [4], header = None, compression = "gzip").values
pmft = pmft.reshape([n_ts, n_z * n_z])
cdft = np.cumsum(pmft, axis = 1)
cdft[:, -1] = 1

for p in range(args.pools):
    pool = np.array([bisect.bisect_left(cdft[args.step], 1 - random.random()) for _ in range(args.size)])
    csv = np.zeros((args.size, 3), dtype=int)
    csv[:, 0] = args.step
    csv[:, 1] = pool
    csv[:, 2] = args.wait
    np.savetxt(os.path.join(args.dir, '{}.csv'.format(p)), csv, fmt='%d', delimiter=',')
