#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy
import socket
print('Host:', socket.gethostname())

ROOTDIR = '/opt/ibm/ILOG/CPLEX_Studio201'
if socket.gethostname() == 'mlui02.ific.uv.es':
    ROOTDIR = '/lhome/ext/iiia021/iiia0211/cplex210'
if socket.gethostname() == 'vega.iiia.csic.es':
    ROOTDIR = '/home/filippo.bistaffa/cplex201'

CPLEXDIR        = ROOTDIR + '/cplex'
CONCERTDIR      = ROOTDIR + '/concert'
CPOPTIMIZERDIR  = ROOTDIR + '/cpoptimizer'
SYSTEM          = 'x86-64_linux'
LIBFORMAT       = 'static_pic'

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension(
            'oracle',
            sources = ['oracle.pyx', 'cpp_oracle.cpp'],
            language = 'c++',
            extra_compile_args = [
                '-m64', '-O', '-fPIC', '-fexceptions', '-std=c++17', '-fpermissive', '-w',
                '-DCPLEX', '-DNDEBUG', '-DIL_STD',
                '-Ofast', '-funroll-loops', '-falign-functions=16', '-falign-loops=16'
            ],
            include_dirs = [
                numpy.get_include(),
                CPLEXDIR + '/include',
                CONCERTDIR + '/include',
                CPOPTIMIZERDIR + '/include',
            ],
            libraries = [
                'ilocplex',
                'concert',
                'cplex',
                'cp',
                'dl',
                'm',
            ],
            library_dirs = [
                CPLEXDIR + '/lib/' + SYSTEM + '/' + LIBFORMAT,
                CONCERTDIR + '/lib/' + SYSTEM + '/' + LIBFORMAT,
                CPOPTIMIZERDIR + '/lib/' + SYSTEM + '/' + LIBFORMAT,
            ],
        )
    ]
)
