# -*- coding: utf-8 -*-
"""
pyrwt: A cython wrapper for the Rice Wavelet Toolbox, written in Cython.

Copyright (C) 2012 Amit Aides
Author: Amit Aides <amitibo@tx.technion.ac.il>
URL: <http://bitbucket.org/amitibo/pyrwt>
License: See attached license file
"""
from setuptools import setup
from setuptools.extension import Extension
from distutils.sysconfig import get_python_lib
from Cython.Distutils import build_ext
import numpy as np
import os.path
import sys


NAME = 'pyrwt'
PACKAGE_NAME = 'rwt'
VERSION = '0.2'
DESCRIPTION = 'A cython wrapper for the Rice Wavelet Toolbox'
LONG_DESCRIPTION = """
pyrwt is a python package that uses cython to wrap the
RICE Wavelet Toolbox. It is fast and enables comparing
the results of your python algorithm with the results
of algorithms that use the Matalb toolbox.
"""
AUTHOR = 'Amit Aides'
EMAIL = 'amitibo@tx.technion.ac.il'
URL = "http://bitbucket.org/amitibo/pyrwt"
KEYWORDS = ["wavelets", "wavelet transform", "DWT"]
LICENSE = 'BSD'
CLASSIFIERS = [
    'License :: OSI Approved :: BSD License',
    'Development Status :: 3 - Alpha',
    'Topic :: Scientific/Engineering'
]
IPOPT_ICLUDE_DIRS=[]
IPOPT_ICLUDE_DIRS += [np.get_include()]

def main():
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        license=LICENSE,
        packages=[PACKAGE_NAME],
        cmdclass = {'build_ext': build_ext},
        ext_modules = [
            Extension(
                PACKAGE_NAME + '.' + 'cyrwt',
                [
                    'src/cyrwt.pyx',
                    'src/dwtaxis.c',
                    'src/mdwt_r.c',
                    'src/midwt_r.c',
                    'src/mrdwt_r.c',
                    'src/mirdwt_r.c',
                ],
                include_dirs=IPOPT_ICLUDE_DIRS
            )
        ],
    )


if __name__ == '__main__':
    main()
