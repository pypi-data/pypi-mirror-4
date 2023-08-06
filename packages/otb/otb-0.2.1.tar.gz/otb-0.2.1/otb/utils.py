#!/usr/bin/env python
# -*- coding: utf-8 -*-
# utils.py --- Basic utilities

# Copyright (c) 2011, 2012, 2013  François Orieux <orieux@iap.fr>

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Commentary:

"""Implement various utilities functions.
"""

# code:

import numpy as np
import numpy.linalg as la

__author__ = "François Orieux"
__copyright__ = "Copyright (C) 2011, 2012, 2013 F. Orieux <orieux@iap.fr>"
__credits__ = ["François Orieux"]
__license__ = "mit"
__version__ = "0.1.0"
__maintainer__ = "François Orieux"
__email__ = "orieux@iap.fr"
__status__ = "development"
__url__ = ""
__keywords__ = "fft"


def vech(matrix):
    """The flattend upper triangular part of the matrix"""
    return matrix[np.triu_indices(matrix.shape[0])]


def uvech(vector):
    """A symetric matrix from the flattened upper triangular part"""
    # Compute the size by resolution of equation size = n(n+1)/2
    size = int((np.sqrt(1 + 8 * len(vector)) - 1) / 2)
    # Fill the upper triangular part
    matrix = np.zeros((size, size))
    matrix[np.triu_indices(size)] = vector.ravel()
    # Fill the lower triangular part
    return matrix.T + matrix - np.diag(matrix.diagonal())


def cov2cor(covariance):
    """The correlation from the covariance matrix"""
    std = np.sqrt(np.diag(covariance))[:, np.newaxis]
    return (covariance / std) / std.T


def fim2cor(fim):
    """The correlation from the Fisher Information Matrix"""
    return cov2cor(la.inv(fim))


def fim2crb(fim):
    """The Cramer Rao Bound from the Fisher Information Matrix"""
    return np.sqrt(np.diag(la.inv(fim)))


def gaussian_kernel(width, sigma=4.0):
    """Return a 2D gaussian kernel"""
    assert isinstance(width, int), 'width must be an integer'
    radius = (width - 1) / 2.0
    axis = np.linspace(-radius,  radius,  width).astype(np.float32)
    filterx = np.exp(-axis * axis / (2 * sigma**2))
    return filterx / filterx.sum()


def circshift(inarray, shifts):
    """Shift array circularly.

    Circularly shifts the values in the array `a` by `s`
    elements. Return a copy.

    Parameters
    ----------
    a : ndarray
       The array to shift.

    s : tuple of int
       A tuple of integer scalars where the N-th element specifies the
       shift amount for the N-th dimension of array `a`. If an element
       is positive, the values of `a` are shifted down (or to the
       right). If it is negative, the values of `a` are shifted up (or
       to the left).

    Returns
    -------
    y : ndarray
       The shifted array (elements are copied)

    Examples
    --------
    >>> circshift(np.arange(10), 2)
    array([8, 9, 0, 1, 2, 3, 4, 5, 6, 7])

    """
    # Initialize array of indices
    idx = []

    # Loop through each dimension of the input matrix to calculate
    # shifted indices
    for dim in range(inarray.ndim):
        length = inarray.shape[dim]
        try:
            shift = shifts[dim]
        except IndexError:
            shift = 0  # no shift if not specify

        # Lets start for fancy indexing. First we build the shifted
        # index for dim k. It will be broadcasted to other dim so
        # ndmin is specified
        index = np.mod(np.array(range(length),
                                ndmin=inarray.ndim) - shift,
                       length)
        # Shape adaptation
        shape = np.ones(inarray.ndim)
        shape[dim] = inarray.shape[dim]
        index = np.reshape(index, shape)

        idx.append(index.astype(int))

    # Perform the actual conversion by indexing into the input matrix
    return inarray[idx]
