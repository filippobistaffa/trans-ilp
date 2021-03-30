#cython: language_level=3
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

def oracle(np.ndarray[unsigned int, ndim = 1, mode = "c"] c,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] reqs,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] steps,
           np.ndarray[unsigned int, ndim = 1, mode = "c"] deltas,
           np.ndarray[float, ndim = 1, mode = "c"] distance,
           np.ndarray[float, ndim = 1, mode = "c"] time):
    return cpp_oracle(c.shape[0], &c[0], reqs.shape[0], &reqs[0], &steps[0], &deltas[0], &distance[0], &time[0])
