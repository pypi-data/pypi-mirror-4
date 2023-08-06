#!/usr/bin/env python
# -*- coding: utf-8 -*-
# plotutils.py --- Ploting utilities

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

"""Ploting utilities
"""

# code:

import numpy as np
import matplotlib.pyplot as plt

__author__ = "François Orieux"
__copyright__ = "Copyright (C) 2011, 2012, 2013 F. Orieux <orieux@iap.fr>"
__credits__ = ["François Orieux"]
__license__ = "mit"
__version__ = "0.1.0"
__maintainer__ = "François Orieux"
__email__ = "orieux@iap.fr"
__status__ = "development"
__url__ = ""
__keywords__ = "plotting"


# Common setup for matplotlib
params = {'backend': 'pdf',
          'savefig.dpi': 300, # save figures to 300 dpi
          'axes.labelsize': 10,
          'text.fontsize': 10,
          'legend.fontsize': 10,
          'xtick.labelsize': 10,
          'ytick.major.pad': 6,
          'xtick.major.pad': 6,
          'ytick.labelsize': 10,
          'text.usetex': True,
          'font.family':'sans-serif',
          # free font similar to Helvetica
          'font.sans-serif':'FreeSans'}


def specshow(image, **kwargs):
    """Plot the spectrum of an image nicely"""
    fig = plt.imshow(np.fft.fftshift(np.log(np.abs(np.fft.fft2(image,
                                                               **kwargs)))))
    plt.gray()
    return fig


def cm2inch(cm):
    """Centimeters to inches"""
    return 0.393701 * cm 

def inch2cm(inches):
    """Inches to centimeters"""
    return inches / 0.393701 

