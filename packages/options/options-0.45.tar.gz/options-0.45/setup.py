#! /usr/bin/env python

from setuptools import setup, find_packages
from decimal import Decimal
import re

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.split() ]
    
    # The double-mention of l.strip() is yet another fine example of why
    # Python needs en passant aliasing.


setup(
    name='options',
    version=0.45,
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Container for flexible class, instance, and function call options',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/options',
    packages=['options'],
    install_requires=['stuf>=0.9.10', 'six'],
    tests_require = ['tox', 'pytest'],
    zip_safe = True,
    keywords='options config configuration parameters arguments',
    classifiers=linelist("""
        Development Status :: 4 - Beta
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)
