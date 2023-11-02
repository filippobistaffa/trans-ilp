import cython
from cython.parallel import prange

# import both numpy and the Cython declarations for numpy
import numpy as np
cimport numpy as np
from numpy cimport uint32_t

cdef extern from "cpp_oracle.hpp":
    float cpp_oracle(const uint32_t s, const uint32_t *_c,
                     const uint32_t n, const uint32_t *_reqs, const uint32_t *_steps, const uint32_t *_deltas,
                     const float *_distance, const float *_time)

@cython.boundscheck(False)
@cython.wraparound(False)

def oracle(coal,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] reqs,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] steps,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] deltas,
           np.ndarray[float, ndim = 1, mode = "c"] distance,
           np.ndarray[float, ndim = 1, mode = "c"] time):
    cdef nreqs = reqs.shape[0]
    cdef np.ndarray[unsigned int, ndim = 1, mode = "c"] a = np.zeros((5,), dtype = np.uint32)
    
    for j in range(len(coal)):
        a[j] = coal[j]
    return cpp_oracle(len(coal), &a[0], nreqs, &reqs[0], &steps[0], &deltas[0], &distance[0], &time[0])
    
def oracle_(cs,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] reqs,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] steps,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] deltas,
           np.ndarray[float, ndim = 1, mode = "c"] distance,
           np.ndarray[float, ndim = 1, mode = "c"] time):
    cdef ncs = len(cs)
    cdef nreqs = reqs.shape[0]
    cdef np.ndarray[float, ndim = 1, mode = "c"] res = np.zeros((ncs,), dtype = np.float32)
    cdef np.ndarray[unsigned int, ndim = 1, mode = "c"] a = np.zeros((5,), dtype = np.uint32)
    for i in range(ncs):
        c = cs[i]
        for j in range(len(c)):
            a[j] = c[j]
        res[i] = cpp_oracle(len(c), &a[0], nreqs, &reqs[0], &steps[0], &deltas[0], &distance[0], &time[0])
    return res
