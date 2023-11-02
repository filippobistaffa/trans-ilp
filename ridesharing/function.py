import numpy as np
from oracle.oracle import oracle

from parameters import params

NUM_ZONES = params['environment']['num_zones']

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

reqs, steps, deltas = read_pool('./oracle/data/fakeFile.csv')
distance, time = read_data('./oracle/data/gmaps_distance.csv', './oracle/data/gmaps_time.csv')

def characterisic_function(collective, participants):
    collective = collective[collective != -1]
    collective = [p[0] * NUM_ZONES + p[1] for p in participants[collective].cpu().tolist()]
    return oracle(collective, reqs, steps, deltas, distance, time)
