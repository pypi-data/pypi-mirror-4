#!/usr/bin/env python
import twiddle

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='twiddle',
    version=twiddle.__version__,
    description='archive all the twiddles',
    packages=['twiddle'],
    package_data={'': ['LICENSE']},
    include_package_data=True,
    author='Jake Johnson',
    author_email='oyouareatubeo@gmail.com',
    url='http://github.com/oyouareatubeo/twiddle',
    scripts=['twiddle/twiddle'],
)
