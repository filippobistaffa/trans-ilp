import argparse as ap

parser = ap.ArgumentParser()
parser.add_argument('--pool', type=str, help='Original pool (default: pool.json)', default='pool.json')
parser.add_argument('subset', type=str, help='Subset file')
args = parser.parse_args()

with open(args.subset) as file:
    line = file.readline().rstrip()

idxs = [int(l) for l in line.split()]

with open(args.pool) as file:
    pool = file.readlines()
    pool = [l.rstrip() for l in pool]

subset = [pool[i] for i in idxs]
print('\n'.join(subset))
