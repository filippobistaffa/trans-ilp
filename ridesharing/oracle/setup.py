#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

setup(
cmdclass = {'build_ext': build_ext},
ext_modules = [Extension("oracle",
                         sources = ["oracle.pyx", "cpp_oracle.cpp"],
                         language="c++",
                         extra_compile_args = ["-Wno-cpp", "-Wno-unused-function","-Ofast", "-march=native", "-funroll-loops",
                                               "-funsafe-loop-optimizations", "-falign-functions=16", "-falign-loops=16"],
                         include_dirs = [numpy.get_include()])
],
)
