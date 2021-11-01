import argparse as ap
import numpy as np
import subprocess
from subprocess import PIPE
import os
import re

parser = ap.ArgumentParser()
parser.add_argument('--base', type=str, help='Base directory', default='200-pg2')
parser.add_argument('--relative', type=str, help='Relative directory', default='200-mcts-rw')
parser.add_argument('--instances', type=int, help='Number of instances', default=2000)
parser.add_argument('--lines', type=int, nargs=2, help='Which line (starting from the bottom) contains the value', default=(1,1))
args = parser.parse_args()

results = np.zeros((2, args.instances))

def extract_float(string):
    m = re.findall(r"[-+]?\d*\.?\d+|[-+]?\d+", string)
    return float(m[0])

def n_to_last_line(filename, n=1):
    ps = subprocess.run(['tail', '-n', str(n), filename], check=True, stdout=PIPE, stderr=PIPE)
    out = subprocess.run(['head', '-n', '1'], input=ps.stdout, stdout=PIPE, stderr=PIPE).stdout.decode().rstrip()
    return out

for i in range(args.instances):
    filename = os.path.join(args.base, '{}.stdout'.format(i))
    if os.path.isfile(filename):
        value = extract_float(n_to_last_line(filename, args.lines[0]))
        #print(i, value)
        results[0, i] = value
    else:
        print('Base, instance {}: missing'.format(i))
        quit()

for i in range(args.instances):
    filename = os.path.join(args.relative, '{}.stdout'.format(i))
    if os.path.isfile(filename):
        value = extract_float(n_to_last_line(filename, args.lines[1]))
        #print(i, value)
        results[1, i] = value
    else:
        print('Relative, instance {}: missing'.format(i))
        quit()

print('[B] Overall mean:', np.mean(results[0]))
print('[R] Overall mean:', np.mean(results[1]))
division = np.divide(results[1], results[0])
print('Relative quality: {}, {}'.format(np.mean(division), np.std(division)))
