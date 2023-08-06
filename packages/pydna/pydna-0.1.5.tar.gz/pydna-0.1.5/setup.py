#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Read version numbers, author etc..
__version__ = "Undefined"
for line in open('pydna/__init__.py'):
    if line.startswith('__'):
        exec(line.strip())

# Change line ending to windows for all text files
import os
for root, dirs, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
    for name in files:
        if not name.lower().endswith(".txt"):
            continue
        filename = os.path.join(root, name)
        with open(filename, "rb") as f:
            data = f.read()
        temp = data.replace('\r\n', '\n')
        temp = temp.replace('\r', '\n')
        temp = temp.replace('\n', '\r\n')
        if not data == temp:
            with open(filename, "wb") as f:
                f.write(temp)
                print "changed", filename

from distribute_setup import use_setuptools
use_setuptools()
from setuptools.command.build_ext import build_ext
from setuptools import setup
from setuptools import Extension

from distutils.errors import CCompilerError, DistutilsPlatformError

import textwrap, sys
import numpy



class optional_build_ext(build_ext):
    # This class allows C extension building to fail.
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            _etype, e, _tb = sys.exc_info()
            self._unavailable(e)

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
            global _speedup_available
            _speedup_available = True
        except CCompilerError:
            _etype, e, _tb = sys.exc_info()
            self._unavailable(e)

    def _unavailable(self, exc):
        print('*' * 70)
        print("warning: An optional C extension could not be compiled.")
        print("pydna will work anyway.")
        print('*' * 70)
        print(exc)



setup(  name='pydna',
        version         =__version__,
        author          =__author__,
        author_email    =__email__,
        cmdclass = {'build_ext': optional_build_ext},
        packages=['pydna',
                  'pydna.py_rstr_max',],

        ext_modules=[Extension('pydna.find_sub_strings', ['pydna/findsubstrings_numpy_arrays_cython.c'])],
        #scripts=[],
        url='http://pypi.python.org/pypi/pydna/',
        license='LICENSE.txt',
        description='''Contains classes and code for representing double
                     stranded DNA and functions for simulating homologous
                     recombination between DNA molecules.''',
        long_description=open('README.txt').read(),
        install_requires =[ "networkx>=1.7", "biopython>=1.6",],
        test_suite="run_tests.load_my_tests",
        include_dirs = [numpy.get_include()],
        zip_safe = False,
        keywords = "bioinformatics",
        classifiers = ['Development Status :: 3 - Alpha',
                       'Environment :: Console',
                       'Intended Audience :: Education',
                       'Intended Audience :: Science/Research',
                       'License :: OSI Approved :: BSD License',
                       'Programming Language :: Python :: 2.7',
                       'Topic :: Education',
                       'Topic :: Scientific/Engineering :: Bio-Informatics',]
        )