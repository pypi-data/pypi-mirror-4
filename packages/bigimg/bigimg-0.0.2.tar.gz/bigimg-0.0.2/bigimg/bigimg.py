#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
    bigimg.py
    ~~~~~~~~~

    Script for generating large images. 

    See README.md for examples.

    Created: 2013-02-13 20:08:26 -0800
    Copyright (c) 2013, Stephen A. Balaban <stephen@stephenbalaban.com>

    Copying and distribution of this file, with or without modification,
    are permitted in any medium without royalty provided the copyright
    notice and this notice are preserved.
"""

import sys
import numpy
import scipy.misc
import math
import random
import string
np = numpy

def cleanfn(fname):
    valid = string.ascii_lowercase + string.ascii_uppercase + \
        string.digits
    return ''.join(c for c in fname if c in valid)


def make_image(width, height, function, outfilepng, verbose=False):
    imat = np.fromfunction(function, (width, height), dtype=float)
    if verbose:
        print(imat)
    img = scipy.misc.toimage(imat, high=np.max(imat),
                             low=np.min(imat))
    img.save(outfilepng)
    return imat


def main(w, h, fs, o, gen_name=False, verbose=False):
    f = eval(fs)
    w = int(w)
    h = int(h)

    if verbose:
        print("# Making matrix image of size (%s, %s) with " \
                  "%s mapped elementwise." % (w, h, fs))
    # generate a name using a hash of the function
    if gen_name:
        o = "%s_out.png" % cleanfn(fs)
    make_image(w, h, f, o)


def lossless_random(w, h, fs, o):
    """
    params:
        w - width
        h - height
        fs - function
        o - outfile
    """
    w = int(w)
    h = int(h)
    a = np.random.uniform(0, 2**16 - 1, (w, h)).astype('int32')
    img = scipy.misc.toimage(a, high=np.max(a),
                             low=np.min(a), mode='I')
    img.save(o)



