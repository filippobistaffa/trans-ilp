from transformer.transformer import Transformer
from oracle.oracle import oracle
import argparse as ap
import numpy as np
import time as tm
import itertools
import random
import torch
import os

default = {
    'threshold': 17,
    'generation': 55,
    'tau': 8
}

def reward(idxs):
    return oracle(np.array(idxs, dtype=np.uint32), reqs, steps, deltas, distance, time)

def read_data(distance_matrix_csv, time_matrix_csv):
    distance = np.genfromtxt(distance_matrix_csv, delimiter=',', dtype=np.float32).ravel()
    time = np.genfromtxt(time_matrix_csv, delimiter=',', dtype=np.float32).ravel()
    return distance, time

def read_pool(pool_csv):
    pool = np.genfromtxt(pool_csv, delimiter=',', dtype=np.uint32)
    steps = pool[:,0].copy(order='C')
    reqs = pool[:,1].copy(order='C')
    deltas = pool[:,2].copy(order='C')
    return reqs, steps, deltas

def trans_coal(pool, model):
    idxs = []
    while len(idxs) < args.max_size:
        action = model(pool, idxs)
        if action == -1:
            break
        idxs.append(action)
    if len(idxs) > 1:
        return idxs, reward(idxs)
    else:
        return None, None

def all_coals(n):
    coals = []
    for s in range(2, args.max_size + 1):
        if tm.time() - start_time < args.generation:
            coals.extend(list(itertools.combinations(list(range(n)), s)))
    return coals

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--distance', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_distance.csv'), help='Distance matrix CSV file')
    parser.add_argument('--time', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_time.csv'), help='Time matrix CSV file')
    parser.add_argument('--threshold', type=int, default=default['threshold'], help='Threshold size for complete generation (default = {})'.format(default['threshold']))
    parser.add_argument('--generation', type=int, default=default['generation'], help='Generation time budget in seconds (default = {})'.format(default['generation']))
    parser.add_argument('--tau', type=int, default=default['tau'], help='Tau (default = {})'.format(default['tau']))
    parser.add_argument('--max_size', type=int, default=5, help='Maximum coalition size (default = 5)')
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    args = parser.parse_args()

    # read input data
    reqs_orig, steps_orig, deltas_orig = read_pool(args.pool)
    distance, time = read_data(args.distance, args.time)
    start_time = tm.time()

    candidates = []
    values = []

    # initialize transformer
    model = Transformer(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'transformer', 'transformer_20-50_t720.pth'), args.tau)

    # set PyTorch seed
    torch.manual_seed(args.seed)

    while tm.time() - start_time < args.generation:
        reqs = reqs_orig.copy()
        steps = steps_orig.copy()
        deltas = deltas_orig.copy()
        idxs = list(range(len(reqs)))
        restart = False

        while len(idxs) > args.threshold and tm.time() - start_time < args.generation:
            coal, rw = trans_coal(reqs, model)
            if coal == None:
                restart = True
                break
            if rw > 0:
                sc = sorted([idxs[idx] for idx in coal])
                if sc not in candidates:
                    candidates.append(sc)
                    values.append(rw)
                    #print('{} = {}'.format(sc, rw))
            for idx in sorted(coal, reverse=True):
                reqs = np.delete(reqs, idx)
                del idxs[idx]

        #print('Reached threshold')

        if not restart:
            coals = all_coals(len(reqs))
            for coal in coals:
                sc = sorted([idxs[idx] for idx in coal])
                if sc not in candidates:
                    rw = reward(coal)
                    if (rw) > 0:
                        candidates.append(sc)
                        values.append(rw)
                        #print('{} = {}'.format(sc, rw))

        #print('Finished iteration')

    tuples = sorted(zip(candidates, values), key=lambda item: item[1])
    for (coal, value) in tuples:
        print('{},{}'.format(value, ','.join(str(i) for i in coal)))
