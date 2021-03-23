import pandas as pd
import sys

zones = 63

if __name__ == '__main__':
    pool = pd.read_csv(sys.argv[1], header=None, names=['t', 'req', 'wait'])
    pool['from'] = pool.req // zones
    pool['to'] = pool.req % zones
    centroids = pd.read_csv(sys.argv[2], header=None, names=['latitude', 'longitude', 'name']).reset_index()
    pool = pd.merge(pool, centroids, left_on='from', right_on='index')
    pool = pd.merge(pool, centroids, left_on='to', right_on='index', suffixes=('_from', '_to'))
    pool.drop(columns=['index_from', 'name_from', 'index_to', 'name_to'], inplace=True)
    pool.to_csv(sys.argv[3], header=False, index=False)
