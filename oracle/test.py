import numpy as np
from oracle import oracle
from oracle import OracleData
import sys

data = OracleData('../data/pool.json', '../data/task_english')
team = sys.argv[1:]
value = oracle(np.array(team, dtype=np.uint32), data)
print(value)
