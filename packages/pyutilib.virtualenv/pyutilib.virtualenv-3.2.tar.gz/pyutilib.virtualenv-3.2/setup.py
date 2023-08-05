#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________
#
"""
Setup for pyutilib.virtualenv package
"""

import os
import sys
from setuptools import setup


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    extra['convert_2to3_doctests'] = ['README.txt']

setup(name="pyutilib.virtualenv",
    version='3.2',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://software.sandia.gov/svn/public/pyutilib/pyutilib.virtualenv',
    license = 'BSD',
    platforms = ["any"],
    description = 'PyUtilib utility for building custom virtualenv bootstrap scripts.',
    long_description = read('README.txt'),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Unix Shell',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    packages=['pyutilib', 'pyutilib.virtualenv'],
    keywords=['utility'],
    namespace_packages=['pyutilib'],
    install_requires=['virtualenv'],
    entry_points = """
        [console_scripts]
        vpy_create=pyutilib.virtualenv.installer:main
        vpy_install=pyutilib.virtualenv.vpy_install:main
    """,
    **extra
    )
