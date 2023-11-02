import pandas as pd
import numpy as np
import random
import bisect
from parameters import params

NUM_ZONES = params['environment']['num_zones']

class CDFT:
	def __init__(self):
		self.tsteps = 24 * 60

		pmft = pd.read_csv('./data/pmf_2016-12_day_minute.gz', delimiter=",", usecols=[4], header=None, compression="gzip").values
		pmft = pmft.reshape([self.tsteps, NUM_ZONES * NUM_ZONES])
		
		self.cdft = np.cumsum(pmft, axis=1)
		self.cdft[:, -1] = 1

	def sample(self, size, tstep):
		return [bisect.bisect_left(self.cdft[tstep], random.random()) for _ in range(size)]
