#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

ROOTDIR         = '/opt/ibm/ILOG/CPLEX_Studio201'
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
