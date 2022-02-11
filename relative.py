import argparse as ap
import numpy as np
import subprocess
from subprocess import PIPE
import os
import re

parser = ap.ArgumentParser()
parser.add_argument('--base', type=str, help='Base directory')
parser.add_argument('--relative', type=str, help='Relative directory')
parser.add_argument('--instances', type=int, nargs=2, help='Instances range (inclusive)', default=(0, 199))
parser.add_argument('--lines', type=int, nargs=2, help='Which line (starting from the bottom) contains the value', default=(5, 1))
parser.add_argument('--seeds', type=int, nargs=2, help='Number of seeds', default=(0, 50))
parser.add_argument('--best', help='Show best seeds', action='store_true')
parser.add_argument('--noprogress', help='Hide progress bar', action='store_true')
parser.add_argument('--mean', help='Mean across seeds', action='store_true')
args = parser.parse_args()

def extract_float(string):
    m = re.findall(r"([+-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)?)", string)
    return float(m[0])

def n_to_last_line(filename, n=1):
    ps = subprocess.run(['tail' if n > 0 else 'head', '-n', str(abs(n)), filename], check=True, stdout=PIPE, stderr=PIPE)
    out = subprocess.run(['head' if n > 0 else 'tail', '-n', '1'], input=ps.stdout, stdout=PIPE, stderr=PIPE).stdout.decode().rstrip()
    return out

labels = ['[B]', '[R]']
paths = [args.base, args.relative]
n_instances = args.instances[1] - args.instances[0] + 1
results = [np.zeros((n_instances, max(args.seeds[j], 1))) for j in [0, 1]]
has_tqdm = False

if not args.noprogress:
    try:
        from tqdm import tqdm
        has_tqdm = True
        total = n_instances * (max(args.seeds[0], 1) + max(args.seeds[1], 1))
        bar_format = '{{percentage:3.0f}}% |{{bar}}| {{n:{}d}}/{{total_fmt}} [{{elapsed}}<{{remaining}}]'.format(len(str(total)))
        pbar = tqdm(bar_format=bar_format, total=total)
    except ImportError:
        pass

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
                results[j][k, s] = value
                if has_tqdm:
                    pbar.update(1)
            else:
                print('{}: {} missing'.format(labels[j], filename))
                quit()
        k += 1

if has_tqdm:
    pbar.close()

#print(results[0])
#print(results[1])

seeds = [np.argmax(results[j], axis=1) for j in [0, 1]]
if args.mean:
    results = [np.mean(results[j], axis=1) for j in [0, 1]]
else:
    results = [np.max(results[j], axis=1) for j in [0, 1]]

#print(results[0])
#print(results[1])

for i in [0, 1]:
    print('{}: Overall mean = {:.4f}'.format(labels[i], np.mean(results[i])))
division = np.divide(results[1], results[0])
print('Relative ratio (min, mean ± std, max): {:.4f}, {:.4f} ± {:.4f}, {:.4f}'.format(np.min(division), np.mean(division), np.std(division), np.max(division)))
if args.best:
    for i in [0, 1]:
        if args.seeds[i] > 0:
            print('{}: {}'.format(labels[i], list(seeds[i])))
