#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from distutils.core import setup
#from distutils.extension import Extension
from Cython.Distutils import build_ext

#from setuptools.command.build_ext import build_ext
from setuptools import setup
from setuptools import Extension

import numpy

ext_modules = [Extension('pydna.find_sub_strings',
                         ['pydna/findsubstrings_numpy_arrays_cython.pyx'],
                         include_dirs=[numpy.get_include()])]

setup( cmdclass = {'build_ext': build_ext},
       ext_modules = ext_modules)


