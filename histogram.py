import matplotlib.pyplot as plt
import numpy as np
import fileinput

if __name__ == '__main__':
    values = []
    candidates = []
    for line in fileinput.input():
        tokens = line.split(',')
        values.append(float(tokens.pop(0)))
        candidates.append([int(idx) for idx in tokens])
    #for c, v in zip(candidates, values):
    #    print(v, c)
    #histogram, bins = np.histogram(values, bins=np.linspace(0, 2, num=41))
    plt.hist(values, bins=np.linspace(0, 2, num=201))
    plt.title("Histogram") 
    plt.show()
