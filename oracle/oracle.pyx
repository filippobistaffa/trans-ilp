#cython: language_level=3
import cython
import numpy as np
cimport numpy as np

# C++ includes
from libcpp.string cimport string as cpp_string
from libcpp.vector cimport vector as cpp_vector
from libcpp.map cimport map as cpp_map

# data types
cdef public struct Personality_profile:
    double sn
    double tf
    double ei
    double pj

cdef public struct Agent:
    int id
    int gender
    Personality_profile profile
    cpp_map[cpp_string,double] competence_level

cdef public struct Competence:
    double level
    double importance

cdef public struct Task_type:
    cpp_map[cpp_string,Competence] required_competences

cdef public struct Data:
    cpp_vector[Agent] agents
    cpp_vector[cpp_string] competences
    Task_type task

# import C++ functions
cdef extern from "cpp_oracle.hpp":
    cpp_vector[Agent] cpp_read_agents(const char *filename)

cdef extern from "cpp_oracle.hpp":
    float cpp_oracle(const unsigned int actual_team_size, const unsigned int *team, Data data)

# class needed to pass data around in python
cdef class OracleData:
    cdef Data data

    def __cinit__(self, agents, task):
        self.data.agents = cpp_read_agents(agents)

    def get_data(self):
        return self.data

@cython.boundscheck(False)
@cython.wraparound(False)

def oracle(np.ndarray[unsigned int, ndim = 1, mode = "c"] c, data):
    return cpp_oracle(c.shape[0], &c[0], data.get_data())
