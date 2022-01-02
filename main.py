from oracle.oracle import oracle
from environment import State
from mcts import MCTS
import argparse as ap
import numpy as np
import os

default = {
    'budget': 60,
    'c': 1,
}

def read_data(distance_matrix_csv, time_matrix_csv):
    distance = np.genfromtxt(distance_matrix_csv, delimiter=',', dtype=np.float32).ravel()
    time = np.genfromtxt(time_matrix_csv, delimiter=',', dtype=np.float32).ravel()
    return distance, time

def read_agents(pool_csv):
    return np.genfromtxt(pool_csv, delimiter=',', dtype=np.uint32)

def value(indices, agents):
    if not (0 < len(indices) < 6):
        return -10
    steps = agents[:,0].copy(order='C')
    reqs = agents[:,1].copy(order='C')
    deltas = agents[:,2].copy(order='C')
    return oracle(np.array(indices, dtype=np.uint32), reqs, steps, deltas, distance, time)

if __name__ == '__main__':
    parser = ap.ArgumentParser(
        formatter_class=lambda prog: ap.HelpFormatter(prog, max_help_position=29)
    )
    parser.add_argument('pool', metavar='POOL', type=str, help='Pool file')
    parser.add_argument('--distance', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_distance.csv'), help='Distance matrix CSV file')
    parser.add_argument('--time', type=str, default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'gmaps_time.csv'), help='Time matrix CSV file')
    parser.add_argument('--budget', type=int, default=default['budget'], help='Time budget in seconds (default = {})'.format(default['budget']))
    parser.add_argument('-c', type=float, default=default['c'], help='MCTS c parameter (default = {})'.format(default['c']))
    args = parser.parse_args()

    distance, time = read_data(args.distance, args.time)
    agents = read_agents(args.pool)

    state = State(agents, value)
    mcts = MCTS(state=state, c=args.c)
    iterations = mcts.search(args.budget)

    solution = [str((c, v)) for c, v in mcts.root.best_state.get_coalitions()]
    v = mcts.root.best_state.get_value()

    print('Search iterations: {}'.format(iterations))
    print('Solution:\n{}'.format('\n'.join(solution)))
    print('Value: {}'.format(v))
