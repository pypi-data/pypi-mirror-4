#/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


def lin_interp(self):
    """
    Interp values discarding NaN.

    Parameter
    ------------
    self: 1d numpy array with NaN's

    Returns
    -----------
    nans: (índex of NANs)
    index: (x), a function over the index, converting
          logical indices of NaNs to values of indices.
    """
    nans, x = np.isnan(self), lambda z: z.nonzero()[0]
    self[nans] = np.interp(x(nans), x(~nans), self[~nans])
