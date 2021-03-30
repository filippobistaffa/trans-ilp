#cython: language_level=3

import cython
import numpy as np
cimport numpy as np

cdef extern from "cpp_oracle.hpp":
    float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team,
                     const unsigned int n_of_agents, const void *agents,
                     const unsigned int n_of_competences, const void *competences,
                     const void *task)


cdef class oracle_data:
    cdef unsigned int n_of_agents
    cdef void *agents
    cdef unsigned int n_of_competences
    cdef void *competences
    cdef const void *task

    def __cinit__(self, agents, task):
        pass

@cython.boundscheck(False)
@cython.wraparound(False)

def oracle(np.ndarray[unsigned int, ndim = 1, mode = "c"] c, data):
    cdef unsigned int n_of_agents = data.n_of_agents
    cdef void *agents = <void *>data.agents
    cdef unsigned int n_of_competences = data.n_of_competences
    cdef void *competences = <void *>data.competences
    cdef void *task = <void *>data.task
    return cpp_oracle(c.shape[0], &c[0], n_of_agents, agents, n_of_competences, competences, task)
