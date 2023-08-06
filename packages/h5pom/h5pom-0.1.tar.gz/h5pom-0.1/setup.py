#!/usr/bin/env python

from setuptools import setup
import os

# py.test -f --cov h5pom --cov-report html --doctest-modules tests h5pom README.txt

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='h5pom',
      version='0.1',
      description='An ORM for hdf5 using h5py for basic IO',
      license='BSD',
      author='Joel B. Mohler',
      author_email='joel@kiwistrawberry.us',
      long_description=read('README.txt'),
      url='https://bitbucket.org/jbmohler/h5pom',
      install_requires=['h5py'],
      packages=['h5pom'],
      classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2",
        "Topic :: Database :: Front-Ends",
        "Operating System :: OS Independent"])
