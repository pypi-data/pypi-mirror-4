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


def verno(s):
    """
    Update the version number passed in by extending it to the 
    thousands place and adding 1/1000, then returning that result
    and as a side-effect updating setup.py

    Dangerous, self-modifying, and also, helps keep version numbers
    ascending without human intervention.
    """
    d = Decimal(s)
    increment = Decimal('0.001')
    d = d.quantize(increment) + increment
    dstr = str(d)
    setup = open('setup.py', 'r').read()
    setup = re.sub('verno\(\w*[\'"]([\d\.]+)[\'"]', 'verno("' + dstr + '"', setup)
    open('setup.py', 'w').write(setup)
    return dstr

setup(
    name='options',
    version=verno("0.402"),
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
