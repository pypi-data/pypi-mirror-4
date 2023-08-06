#!/usr/bin/env python

from distutils.core import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='tripcode',
    version='0.1',
    description='Trivial tripcode library',
    long_description=long_description,
    author='Koen Crolla',
    author_email='cairnarvon@gmail.com',
    url='https://github.com/Cairnarvon/tripcode',
    py_modules=['tripcode'],
    classifiers=['License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Topic :: Internet']
)
