#!/usr/bin/env python

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='sdmx',
    version='0.1.0',
    description='Read SDMX XML files',
    long_description=read("README"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/sdmx.py',
    packages=['sdmx'],
    keywords="sdmx",
)

