#!/usr/bin/env python

import os
import sys
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


_install_requires = ["requests>=1.0,<3.0"]
if sys.version_info[:2] < (2, 7):
    _install_requires.append("lxml>=3.2.4,<4.0")
    _install_requires.append("ordereddict>=1.1,<2.0")


setup(
    name='sdmx',
    version='0.2.10',
    description='Read SDMX XML files',
    long_description=read("README.rst"),
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://github.com/mwilliamson/sdmx.py',
    packages=['sdmx'],
    install_requires=_install_requires,
    keywords="sdmx",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ],
)

