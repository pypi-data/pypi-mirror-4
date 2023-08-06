#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(name='BNfinder',
      version='2.0.4',
      author='Bartek Wilczynski and Norbert Dojer',
      author_email='bartek@mimuw.edu.pl',
      url='http://bioputer.mimuw.edu.pl/software/bnf',
      download_url='http://pypi.python.org/pypi/BNfinder/',
      packages=['BNfinder'],
      scripts=['bnf','bnc','bnf-cv'],
      license='GNU GPL v.2',
      description='Bayes Net Finder: an efficient and exact method for learning bayesian networks',
      
      install_requires=[
        "fpconst",
        "scipy",
   ]
     )


