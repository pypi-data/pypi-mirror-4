#!/usr/bin/env python

import os
from distutils.core import setup


setup(
    name='nose-test-sets',
    version='0.1.0',
    description='Create test sets to test different implementations of the same interface',
    author='Michael Williamson',
    url='http://github.com/mwilliamson/spur.py',
    py_modules=["nose_test_sets"],
    install_requires=["nose>=1.0.0,<2"],
)
