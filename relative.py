import argparse as ap
import numpy as np
import subprocess
from subprocess import PIPE
import os
import re

parser = ap.ArgumentParser()
parser.add_argument('--base', type=str, help='Base directory')
parser.add_argument('--relative', type=str, help='Relative directory')
parser.add_argument('--instances', type=int, nargs=2, help='Instances range (inclusive)', default=(0, 499))
parser.add_argument('--lines', type=int, nargs=2, help='Which line (starting from the bottom) contains the value', default=(1,1))
parser.add_argument('--seeds', type=int, nargs=2, help='Number of seeds', default=(0,0))
parser.add_argument('--best', help='Show best seeds', action='store_true')
args = parser.parse_args()

results = np.zeros((2, args.instances[1] - args.instances[0] + 1))
seeds = np.zeros((2, args.instances[1] - args.instances[0] + 1), dtype=int)

def extract_float(string):
    m = re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", string)
    return float(m[0])

def n_to_last_line(filename, n=1):
    ps = subprocess.run(['tail', '-n', str(n), filename], check=True, stdout=PIPE, stderr=PIPE)
    out = subprocess.run(['head', '-n', '1'], input=ps.stdout, stdout=PIPE, stderr=PIPE).stdout.decode().rstrip()
    return out

labels=['[B]', '[R]']
paths = [args.base, args.relative]

for j in [0, 1]:
    k = 0
    for i in range(args.instances[0], args.instances[1] + 1):
        for s in range(max(args.seeds[j], 1)):
            if args.seeds[j] > 0:
                filename = os.path.join(paths[j], '{}-{}.stdout'.format(i, s))
            else:
                filename = os.path.join(paths[j], '{}.stdout'.format(i))
            if os.path.isfile(filename):
                value = extract_float(n_to_last_line(filename, args.lines[j]))
                #print(value)
                if value > results[j, k]:
                    results[j, k] = value
                    seeds[j, k] = s
            else:
                print('{}: {} missing'.format(labels[j], filename))
                quit()
        #print(i, results[j, k])
        k += 1

for i in [0, 1]:
    print('{}: Overall mean = {:.4f}'.format(labels[i], np.mean(results[i])))
division = np.divide(results[1], results[0])
print('Relative quality (min, mean ± std, max): {:.4f}, {:.4f} ± {:.4f}, {:.4f}'.format(np.min(division), np.mean(division), np.std(division), np.max(division)))
if args.best:
    for i in [0, 1]:
        if args.seeds[i] > 0:
            print('{}: {}'.format(labels[i], list(seeds[i])))
