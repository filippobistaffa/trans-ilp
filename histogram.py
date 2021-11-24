import matplotlib.pyplot as plt
import argparse as ap
import numpy as np
import fileinput
import sys

if __name__ == '__main__':
    parser = ap.ArgumentParser()
    parser.add_argument('file', nargs='?', type=ap.FileType('r'), default=sys.stdin)
    parser.add_argument('--ylim', type=int)
    args = parser.parse_args()
    values = []
    candidates = []
    lines = args.file.readlines()
    lines = [line.rstrip() for line in lines]
    for line in lines:
        tokens = line.split(',')
        values.append(float(tokens.pop(0)))
        candidates.append([int(idx) for idx in tokens])
    #for c, v in zip(candidates, values):
    #    print(v, c)
    #histogram, bins = np.histogram(values, bins=np.linspace(0, 2, num=41))
    plt.hist(values, bins=np.linspace(0, 2, num=201))
    plt.ylim((None, args.ylim))
    plt.title("Histogram") 
    plt.show()
