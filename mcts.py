from oracle.oracle import oracle
from oracle.oracle import OracleData
from tree import MCTS, Node
import numpy as np
import random
import os

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

    def reward(self):
        if len(self.idxs) > 0:
            return oracle(np.array(self.idxs, dtype=np.uint32), data)
        else:
            return 0

    def is_terminal(self):
        return self.terminal

    def add_idx(self, idx): # assumes idx not in self.idxs
        if idx == -1:
            return Coalition(idxs=self.idxs, terminal=True)
        idxs = self.idxs.copy()
        idxs.append(idx)
        return Coalition(idxs=idxs, terminal=len(idxs) == max_size)

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


import argparse as ap

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--max_size', type=int, default=5, help='Maximum coalition size (default = 5)')
    parser.add_argument('--task', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'task_english'), help='Task input file')
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    parser.add_argument('--uct', type=float, default=50, help='UCT weight (default = 50)')
    parser.add_argument('--exploration', type=float, default=0.1, help='Exploration weight (default = 0.1)')
    parser.add_argument('--complete', help='Force complete coalitions', action="store_true")
    parser.add_argument('--irace', help='Print value for IRACE optimisation', action="store_true")
    required = parser.add_mutually_exclusive_group(required=True)
    required.add_argument('--iterations', type=int, help='Number of iterations')
    required.add_argument('--budget', type=int, help='Time budget in seconds')
    args = parser.parse_args()

    # set global variables
    max_size = args.max_size
    partial = not args.complete
    random.seed(args.seed)

    # read input data
    data = OracleData(args.pool, args.task)
    all_idxs = list(range(data.pool_size()))

    # initialise MCTS tree
    tree = MCTS(
        Coalition(idxs=[], terminal=False),
        budget=args.budget,
        iterations=args.iterations,
        exploration_rate=args.exploration,
        uct_weight=args.uct
    )

    # execute MCTS algorithm
    tree.run()

    # print terminal nodes' values    
    terminal = sorted(filter(lambda item: item[0].is_terminal(), tree.A.items()), key=lambda item: item[1])
    for item in terminal:
        print('{},{}'.format(item[1],','.join(str(idx) for idx in item[0].idxs)))

    # print value for IRACE if necessary
    if args.irace:
        if len(terminal) > 0:
            print(-terminal[-1][1])
        else:
            print(10000) # high cost as penalty
