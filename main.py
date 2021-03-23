from oracle.oracle import oracle
from mcts import MCTS, Node
import numpy as np
import random

max_size = 5
partial = False

class Coalition(Node):
    def __init__(self, idxs, terminal):
        self.idxs = idxs
        self.terminal = terminal

    def find_children(self):
        if self.terminal:
            return []
        remaining = [i for i in all_idxs if not self.idxs or i > max(self.idxs)]
        if partial:
            if len(self.idxs) > 0:
                remaining.append(-1)
        children = [self.add_idx(idx) for idx in remaining]
        return [child for child in children if child is not None]

    def find_random_child(self):
        remaining = [i for i in all_idxs if not self.idxs or i > max(self.idxs)]
        if partial:
            if len(self.idxs) > 0:
                remaining.append(-1)
        if not remaining:
            return None
        else:
            return self.add_idx(random.choice(remaining))

    def find_myopic_child(self):
        if self.terminal:
            return []
        remaining = [i for i in all_idxs if not self.idxs or i > max(self.idxs)]
        if partial:
            if len(self.idxs) > 0:
                remaining.append(-1)
        if not remaining:
            return None
        children = [self.add_idx(idx) for idx in remaining]
        def gain(node):
            return node.reward() #- self.reward()
        return max(children, key=gain)

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
    parser = ap.ArgumentParser()
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool CSV file')
    parser.add_argument('--distance', type=str, default='data/gmaps_distance.csv', help='Distance matrix CSV file')
    parser.add_argument('--time', type=str, default='data/gmaps_time.csv', help='Time matrix CSV file')
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    parser.add_argument('--iterations', type=int, default=10000, help='Number of iterations (default = 10000)')
    parser.add_argument('--uct', type=float, default=1, help='UCT weight (default = 1)')
    parser.add_argument('--exploration', type=float, default=0.1, help='Exploration weight (default = 0.1)')
    args = parser.parse_args()

    random.seed(args.seed)
    reqs, steps, deltas = read_pool(args.pool)
    distance, time = read_data(args.distance, args.time)
    all_idxs = list(range(len(reqs)))
    root = Coalition(idxs=[], terminal=False)
    rewards = dict()
    #dfs(root, rewards)
    #print('DFS')
    #print(*sorted(rewards.items(), key=lambda item: item[1]), sep='\n')
    tree = MCTS(
        root,
        exploration_rate=args.exploration,
        uct_weight=args.uct
    )
    tree.run()
    terminal = sorted(filter(lambda item: item[0].is_terminal(), tree.A.items()), key=lambda item: item[1])
    #print('MCTS')
    for item in terminal:
        print(item[0], item[1])
    print(-terminal[-1][1])
