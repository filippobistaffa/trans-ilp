from environment_improved import State as State_improved
from mcts_improved import MCTS as MCTS_improved

from environment import State
from mcts import MCTS

from oracle.oracle import *
import argparse as ap
import numpy as np
import random
import math
import os

default = {
    'budget': 60,
    'c': 1,
    'k': 5.43,
    'g': 0.9
}

def value(indices, agents):
    if len(indices) != 5:
        return -10
    return np.log(oracle(np.array(indices, dtype=np.uint32), data, agents))

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--task', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'task_english'), help='Task input file')
    parser.add_argument('--budget', type=int, default=default['budget'], help='Time budget in seconds (default = {})'.format(default['budget']))
    parser.add_argument('--seed', type=int, default=0, help='Seed (default = 0)')
    parser.add_argument('-c', type=float, default=default['c'], help='MCTS c parameter (default = {})'.format(default['c']))
    parser.add_argument('-k', type=float, default=default['k'], help='MCTS k parameter (default = {})'.format(default['k']))
    parser.add_argument('-g', type=float, default=default['g'], help='MCTS gamma parameter (default = {})'.format(default['g']))
    parser.add_argument('--improved', help='Use improved version', action='store_true')
    args = parser.parse_args()

    random.seed(args.seed)
    data = OracleData(args.task)
    agents = read_agents(args.pool)

    if args.improved:
        state = State_improved(agents, value)
        mcts = MCTS_improved(state=state, c=args.c, k=args.k, gamma=args.g)
    else:
        state = State(agents, value)
        mcts = MCTS(state=state, c=args.c)
    iterations = mcts.search(args.budget)
    solution = [str((c, math.exp(v))) for c, v in mcts.root.best_state.get_coalitions()]
    v = mcts.root.best_state.get_value()

    print('Search iterations: {}'.format(iterations))
    print('Solution:\n{}'.format('\n'.join(solution)))
    print('Value: {}'.format(math.exp(v)))
