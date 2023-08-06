#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    bigimg
    ~~~~~~
"""

from distutils.core import setup

setup(
    name='bigimg',
    version='0.0.2',
    url='http://github.com/stephenbalaban/bigimg',
    author='Stephen Balaban',
    author_email='stephen@stephenbalaban.com',
    packages=[
        'bigimg',
        'test',
        ],
    platforms='any',
    scripts=['scripts/bigimg'],
    license='LICENSE',
    requires=[
        'scipy (>= 0.9.0)',
        'numpy',
        ],
    description="bigimg lets you generate big images with just a lambda expression.",
    long_description=open('README.md').read(),
)
