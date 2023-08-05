#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='twiddle',
    version='0.0.2',
    description='archive all the twiddles',
    author='Jake Johnson',
    author_email='oyouareatubeo@gmail.com',
    url='http://github.com/oyouareatubeo/twiddle',
    include_package_data=True,
    scripts=['twiddle'],
)
