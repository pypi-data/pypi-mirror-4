#!/usr/bin/env python

import numpy as np
import nose
from nose.tools import *
from stsci.image import combine


arrays = []
def setup_module():
    global arrays
    a = np.arange(4).reshape((2, 2))
    arrays = [a * 16, a * 4, a * 2, a * 8]


def test_minimum1():
    """
    minimum() nominally computes the minimum pixel value for a stack of
    identically shaped images.

    arrays     specifies a sequence of inputs arrays, which are nominally a
               stack of identically shaped images.

    output     may be used to specify the output array.  If none is specified,
               either arrays[0] is copied or a new array of type 'outtype'
               is created.

    outtype    specifies the type of the output array when no 'output' is
               specified.

    nlow       specifies the number of pixels to be excluded from minimum
               on the low end of the pixel stack.

    nhigh      specifies the number of pixels to be excluded from minimum
               on the high end of the pixel stack.

    badmasks   specifies boolean arrays corresponding to 'arrays', where true
               indicates that a particular pixel is not to be included in the
               minimum calculation.
    """

    result = combine.minimum(arrays)
    expected = np.array([[0, 2],
                         [4, 6]])
    assert_true((result == expected).all())


def test_minimum2():
    result = combine.minimum(arrays, nhigh=1)
    expected = np.array([[0, 2],
                         [4, 6]])
    assert_true((result == expected).all())


def test_minimum3():
    result = combine.minimum(arrays, nlow=1)
    expected = np.array([[ 0,  4],
                         [ 8, 12]])
    assert_true((result == expected).all())


def test_minimum4():
    result = combine.minimum(arrays, outtype=np.float32)
    expected = np.array([[ 0.,  2.],
                         [ 4.,  6.]], dtype=np.float32)
    assert_true((result == expected).all())


def test_minimum5():
    bm = np.zeros((4,2,2), dtype=np.bool8)
    bm[2,...] = 1
    result = combine.minimum(arrays, badmasks=bm)
    expected = np.array([[ 0,  4],
                         [ 8, 12]])
    assert_true((result == expected).all())


def test_minimum6():
    result = combine.minimum(arrays,
                             badmasks=combine.threshhold(arrays, low=10))
    expected = np.array([[ 0, 16],
                         [16, 12]])
    assert_true((result == expected).all())
