#!/usr/bin/env python
from setuptools import setup, find_packages
import sys, os

VERSION = '0.0.1'

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

current_wd = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(current_wd , 'README.txt')).read()

setup(name='pyLICORS',
      version=VERSION,
      description="A Python interface for predictive state estimation from spatio-temporal data",
      long_description=README,
      classifiers=['Development Status :: 1 - Planning',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Scientific/Engineering'
                  ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='forecasting spatio-temporal nonparametric statistics estimation',
      author='Georg M. Goerg',
      author_email='my_three_initials@stat.cmu.edu',
      url='www.stat.cmu.edu/~gmg',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'test', 'notyet', 'dist', 'docs_old']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['docutils>=0.3', 
                        'numpy>=1.5',
                        'scikit-learn>=0.1'
                        ]
      )
