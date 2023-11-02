import numpy as np
from oracle.oracle import oracle

def carachteristic_function(oracle_data, indices, participants):
    return oracle(np.array(list(map(str, indices.tolist())), dtype=np.uint32), oracle_data, participants)
