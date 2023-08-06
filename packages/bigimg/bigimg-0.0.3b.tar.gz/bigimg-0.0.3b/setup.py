#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
bigimg
======

Easily create big images. With just a lambda expression.

An image can be seen as a function that maps a real-valued (x, y)
coordinate onto a color. With this in mind, I made bigimg.

``bigimg.py`` allows you to define a canvas width and height, a vector
function which will conduct an element wise map over each element in the
canvas, and an output file. If your function returns a single floating
point value, the resulting image will be gray scale, if it returns a
3-tuple, it will be color.

Installation
------------

::

    $ git clone https://github.com/stephenbalaban/bigimg.git
    $ cd bigimg
    $ sudo pip install -e .

You can also create pseudorandom images with:

.. code:: bash

    ./bigimg 128 128 pseudorandom.png --lambda random

This is useful in a variety of contexts.

Examples
--------

Check out the example images included. You can pull request a new
example image if you find an especially cool formula. Simply add the
code to the example set below, and place the image in the examples/
folder.

Only the best images, as determined by me, will be accepted.

Grayscale
~~~~~~~~!

::

    bigimg 512 512 examples/1.png --lambda "lambda x, y: 2048. * np.sin(x/32.) + 2048. * np.sin(y/32.)"

.. figure:: examples/1.png
   :alt: lambda x, y: 2048. * np.sin(x/32.) + 2048. * np.sin(y/32.)

   Example 1
::

    bigimg 512 512 examples/2.png --lambda "lambda x, y: y * np.cos(x/128.)"

.. figure:: examples/2.png
   :alt: lambda x, y: y * np.cos(x/128.)

   Example 2
::

    bigimg 512 512 --lambda random examples/0.png

.. figure:: examples/0.png
   :alt: random

   Example 0
Color
~~~~~

::

    bigimg 512 512 examples/3.png --lambda "lambda x, y: (x, x, y)"

.. figure:: examples/3.png
   :alt: lambda x, y: (x, x, y)

   Example 3
::

    bigimg 512 512 examples/4.png --lambda "lambda x, y: (x, np.sin(x), np.sin(y))"

.. figure:: examples/4.png
   :alt: lambda x, y: (x, np.sin(x), np.sin(y))

   Example 4
::

    bigimg 1024 1024 examples/5.png --lambda "lambda x, y: (512 * np.cos(y/32.), 512 * np.sin(x/32.), 512 * np.sin(y/32.))"

.. figure:: examples/5.png
   :alt: lambda x, y: (512 * np.cos(y/32.), 512 * np.sin(x/32.), 512 * np.sin(y/32.))

   Example 5

"""

from distutils.core import setup

setup(
    name='bigimg',
    version='0.0.3b',
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
    install_requires=[
        'scipy>=0.9.0',
        'numpy',
        ],
    description="bigimg lets you generate big images with just a lambda expression.",
    long_description=__doc__
)
