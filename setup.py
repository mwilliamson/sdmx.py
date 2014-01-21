#!/usr/bin/env python

import os
import sys
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


_install_requires = []
if sys.version_info[:2] < (2, 7):
    _install_requires.append("lxml>=3.2.4,<4.0")
    _install_requires.append("ordereddict>=1.1,<2.0")


setup(
    name='sdmx',
    version='0.2.4',
    description='Read SDMX XML files',
    long_description=read("README"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/sdmx.py',
    packages=['sdmx'],
    install_requires=_install_requires,
    keywords="sdmx",
)

