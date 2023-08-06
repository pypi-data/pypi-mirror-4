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
Script to generate the installer for pyutilib.svn.
"""

import sys
if sys.version_info[0:2] < (2,5):
    print("ERROR: PyYAML is not available for Python version before 2.5")
    print("ERROR: Aborting installation of pyutilib.svn")
    sys.exit(0)

import os
import glob
from setuptools import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name="pyutilib.svn",
    version='1.4',
    maintainer='William E. Hart',
    maintainer_email='wehart@sandia.gov',
    url = 'https://software.sandia.gov/svn/public/pyutilib/pyutilib.svn',
    license = 'BSD',
    platforms = ["any"],
    description = 'A PyUtilib package for subversion-related utilities.',
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
        'Topic :: Software Development :: Libraries :: Python Modules'],
    packages=['pyutilib', 'pyutilib.svn'],
    keywords=['utility'],
    namespace_packages=['pyutilib'],
    entry_points = """
        [console_scripts]
        svnpm=pyutilib.svn.svnpm:main
        svn-timemachine=pyutilib.svn.svn_timemachine:main
    """
    )
