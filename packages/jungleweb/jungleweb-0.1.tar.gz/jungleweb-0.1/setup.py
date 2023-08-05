#!/usr/bin/env python

from distutils.core import setup

setup(
    name='jungleweb',
    version='0.1',
    description='Utilities for storing webpage summary information',
    author='Martin Atkins',
    author_email='mart@degeneration.co.uk',
    packages=['jungleweb'],
    url="https://github.com/apparentlymart/python-jungleweb",
    requires=[
        'sqlalchemy',
        'opengraph',
        'publicsuffix',
        'ghost.py',
    ],
)
