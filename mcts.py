from oracle.oracle import oracle
from tree import MCTS, Node
import numpy as np
import time as tm
import random
import os

class Coalition(Node):
    def __init__(self, idxs, terminal):
        self.idxs = idxs
        self.terminal = terminal

    def remaining(self):
        return [i for i in all_idxs if not self.idxs or i > max(self.idxs)]

    def find_children(self):
        if self.terminal:
            return []
        remaining = self.remaining()
        if partial:
            if len(self.idxs) > 0:
                remaining.append(-1)
        children = [self.add_idx(idx) for idx in remaining]
        return [child for child in children if child is not None]

    def find_random_child(self):
        remaining = self.remaining()
        if partial:
            if len(self.idxs) > 0:
                remaining.append(-1)
        if not remaining:
            return None
        else:
            return self.add_idx(random.choice(remaining))

    def reward(self):
        if len(self.idxs) > 0:
            return oracle(np.array(self.idxs, dtype=np.uint32), reqs, steps, deltas, distance, time)
        else:
            return 0

    def is_terminal(self):
        return self.terminal

    def add_idx(self, idx): # assumes idx not in self.idxs
        if idx == -1:
            return Coalition(idxs=self.idxs, terminal=True)
        idxs = self.idxs.copy()
        idxs.append(idx)
        min_tpd = min(steps[idxs] + deltas[idxs])
        max_t = max(steps[idxs])
        if min_tpd >= max_t:
            return Coalition(idxs=idxs, terminal=len(idxs) == max_size)
        else:
            return None

    def __repr__(self):
        return str(self.idxs)

    def __lt__(self, other):
        return self.idxs < other.idxs


def dfs(coal, rewards):
    #print('Visiting', coal.idxs)
    if coal.terminal:
        reward = coal.reward()
        rewards[coal] = reward
    else:
        for child in coal.find_children():
            dfs(child, rewards)


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


import argparse as ap

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--iterations', type=int, default=5000, help='Number of iterations (default = 1000)')
    parser.add_argument('--budget', type=int, default=40, help='Time budget in seconds (default = 40)')
    parser.add_argument('--max_size', type=int, default=5, help='Maximum coalition size (default = 5)')
    parser.add_argument('--distance', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_distance.csv'), help='Distance matrix CSV file')
    parser.add_argument('--time', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_time.csv'), help='Time matrix CSV file')
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    parser.add_argument('--uct', type=float, default=50, help='UCT weight (default = 50)')
    parser.add_argument('--exploration', type=float, default=0.1, help='Exploration weight (default = 0.1)')
    parser.add_argument('--complete', help='Force complete coalitions', action="store_true")
    parser.add_argument('--irace', help='Print value for IRACE optimisation', action="store_true")
    args = parser.parse_args()

    # set global variables
    max_size = args.max_size
    partial = not args.complete
    random.seed(args.seed)

    # read input data
    reqs, steps, deltas = read_pool(args.pool)
    distance, time = read_data(args.distance, args.time)
    all_idxs = list(range(len(reqs)))
    start_time = tm.time()

    while args.budget > tm.time() - start_time:
        # initialise MCTS tree
        tree = MCTS(
            Coalition(idxs=[], terminal=False),
            iterations=args.iterations,
            exploration_rate=args.exploration,
            uct_weight=args.uct
        )
        # execute MCTS algorithm
        terminal = tree.run()
        # get best candidate
        best = terminal[-1]
        print('{},{}'.format(best[1], ','.join(str(idx) for idx in best[0].idxs)))
        all_idxs = [idx for idx in all_idxs if idx not in best[0].idxs]

    # print value for IRACE if necessary
    if args.irace:
        pass
