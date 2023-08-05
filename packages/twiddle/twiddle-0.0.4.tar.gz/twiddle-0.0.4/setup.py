#!/usr/bin/env python
import sys
import os

import twiddle

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = [
    'PyYAML>=3.10',
    'pymongo>=2.4.1',
    'tweetstream>=1.1.1',
]

setup(
    name='twiddle',
    version=twiddle.__version__,
    description='archive all the twiddles',
    packages=['twiddle'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requires,
    author='Jake Johnson',
    author_email='oyouareatubeo@gmail.com',
    url='http://github.com/oyouareatubeo/twiddle',
    scripts=['twiddle/twiddle'],
)
