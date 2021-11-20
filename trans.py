from transformer.transformer import Transformer
from oracle.oracle import oracle
from oracle.oracle import OracleData
import argparse as ap
import numpy as np
import time as tm
import itertools
import random
import torch
import os

default = {
    'threshold': 15,
    'generation': 50,
    'lambda': 0.8,
    'entropy': 0.05
}

def reward(idxs):
    return oracle(np.array(idxs, dtype=np.uint32), args.l, data)

def select_key(keys, n):
    idx = (np.abs(keys - n)).argmin()
    #print('Closest to {} is {}'.format(n, keys[idx]))
    return keys[idx]

def trans_coal(pool, model):
    idxs = []
    while len(idxs) < args.size:
        action = model(pool, idxs)
        idxs.append(action)
    return idxs, reward(idxs)

def all_coals(n):
    return itertools.combinations(list(range(n)), args.size)

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--task', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'task_english'), help='Task file')
    parser.add_argument('--lambda', dest='l', type=float, default=default['lambda'], help='Lambda parameter (default = {})'.format(default['lambda']))
    parser.add_argument('--threshold', type=int, default=default['threshold'], help='Threshold size for complete generation (default = {})'.format(default['threshold']))
    parser.add_argument('--generation', type=int, default=default['generation'], help='Generation time budget in seconds (default = {})'.format(default['generation']))
    parser.add_argument('--size', type=int, default=5, help='Coalitions\' size (default = 5)')
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    parser.add_argument('--entropy', type=float, default=default['entropy'], help='Transformer\'s entropy value (default = {})'.format(default['entropy']))
    args = parser.parse_args()

    # read input data
    data_orig = OracleData(args.pool, args.task)
    start_time = tm.time()

    candidates = []
    values = []

    # initialize transformers
    models = {
        50: Transformer(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'transformer', 'transformer_50_entropy{:.2f}_lambda{:.1f}.pth'.format(args.entropy, args.l)))
    }
    keys = np.asarray(list(models.keys()))

    # set PyTorch seed
    torch.manual_seed(args.seed)

    while tm.time() - start_time < args.generation:
        data = data_orig.copy()
        idxs = list(range(data.pool_size()))
        restart = False

        while len(idxs) > args.threshold and tm.time() - start_time < args.generation:
            coal, rw = trans_coal(data.get_pool(), models[select_key(keys, len(idxs))])
            if coal == None:
                restart = True
                break
            sc = sorted([idxs[idx] for idx in coal])
            if sc not in candidates:
                candidates.append(sc)
                values.append(rw)
                #print('{} = {}'.format(sc, rw))
            for idx in sorted(coal, reverse=True):
                data.remove_idx(idx)
                del idxs[idx]

        #print('Reached threshold')

        if not restart and tm.time() - start_time < args.generation:
            coals = all_coals(len(idxs))
            for coal in coals:
                sc = sorted([idxs[idx] for idx in coal])
                if sc not in candidates and tm.time() - start_time < args.generation:
                    rw = reward(coal)
                    candidates.append(sc)
                    values.append(rw)
                    #print('{} = {}'.format(sc, rw))

        #print('Finished iteration')

    tuples = sorted(zip(candidates, values), key=lambda item: item[1])
    for (coal, value) in tuples:
        print('{},{}'.format(value, ','.join(str(i) for i in coal)))
