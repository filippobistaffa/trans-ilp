import argparse as ap
import numpy as np
import subprocess
import os

parser = ap.ArgumentParser()
parser.add_argument('--base', type=str, help='Base directory', default='pg2')
parser.add_argument('--relative', type=str, help='Relative directory', default='mcts-rw')
parser.add_argument('--instances', type=int, help='Number of instances', default=2000)
parser.add_argument('--repetitions', type=int, help='Number of repetitions', default=10)
args = parser.parse_args()

results = np.zeros((2, args.instances, args.repetitions))

def last_line(filename):
    return subprocess.check_output(['tail', '-1', filename]).rstrip()
    #with open(filename, 'r') as f:
    #    lines = f.read().splitlines()
    #    last_line = lines[-1]
    #return last_line.rstrip()

for i in range(args.instances):
    for r in range(args.repetitions):
        filename = os.path.join(args.base, '{}-{}.stdout'.format(i, r))
        if len(filename):
            value = float(last_line(filename))
            #print(i, r, value)
            results[0, i, r] = value
        else:
            print('Base, instance {}, repetition {}: missing')
            quit()

for i in range(args.instances):
    for r in range(args.repetitions):
        filename = os.path.join(args.relative, '{}-{}.stdout'.format(i, r))
        if len(filename):
            value = float(last_line(filename))
            #print(i, r, value)
            results[1, i, r] = value
        else:
            print('Relative, instance {}, repetition {}: missing')
            quit()

mean = np.mean(results, axis=2)
division = np.divide(mean[1], mean[0])
print(np.mean(division))
