import argparse as ap
import numpy as np
import subprocess
from subprocess import PIPE
import os
import re

parser = ap.ArgumentParser()
parser.add_argument('--base', type=str, help='Base directory', default='200-pg2')
parser.add_argument('--relative', type=str, help='Relative directory', default='200-mcts-rw')
parser.add_argument('--instances', type=int, nargs=2, help='Instances range (inclusive)', default=(0, 499))
parser.add_argument('--lines', type=int, nargs=2, help='Which line (starting from the bottom) contains the value', default=(1,1))
parser.add_argument('--seeds', type=int, nargs=2, help='Number of seeds', default=(0,0))
args = parser.parse_args()

results = np.zeros((2, args.instances[1] - args.instances[0] + 1))

def extract_float(string):
    m = re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", string)
    return float(m[0])

def n_to_last_line(filename, n=1):
    ps = subprocess.run(['tail', '-n', str(n), filename], check=True, stdout=PIPE, stderr=PIPE)
    out = subprocess.run(['head', '-n', '1'], input=ps.stdout, stdout=PIPE, stderr=PIPE).stdout.decode().rstrip()
    return out

k = 0
for i in range(args.instances[0], args.instances[1] + 1):
    for s in range(max(args.seeds[0], 1)):
        if args.seeds[0] > 0:
            filename = os.path.join(args.base, '{}-{}.stdout'.format(i, s))
        else:
            filename = os.path.join(args.base, '{}.stdout'.format(i))
        if os.path.isfile(filename):
            value = extract_float(n_to_last_line(filename, args.lines[0]))
            #print(value)
            results[0, k] = max(value, results[0, k])
        else:
            print('Base, {}: missing'.format(filename))
            quit()
    #print(i, results[0, k])
    k += 1

k = 0
for i in range(args.instances[0], args.instances[1] + 1):
    for s in range(max(args.seeds[1], 1)):
        if args.seeds[1] > 0:
            filename = os.path.join(args.relative, '{}-{}.stdout'.format(i, s))
        else:
            filename = os.path.join(args.relative, '{}.stdout'.format(i))
        if os.path.isfile(filename):
            value = extract_float(n_to_last_line(filename, args.lines[1]))
            #print(value)
            results[1, k] = max(value, results[1, k])
        else:
            print('Relative, {}: missing'.format(filename))
            quit()
    #print(i, results[1, k])
    k += 1

print('[B] Overall mean: {:.4f}'.format(np.mean(results[0])))
print('[R] Overall mean: {:.4f}'.format(np.mean(results[1])))
division = np.divide(results[1], results[0])
print('Relative quality (min, mean ± std, max): {:.4f}, {:.4f} ± {:.4f}, {:.4f}'.format(np.min(division), np.mean(division), np.std(division), np.max(division)))
