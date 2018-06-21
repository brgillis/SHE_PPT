""" @file math.py

    Created 12 February, 2018

    Miscellaneous mathematical functions
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import numpy as np


class LinregressStatistics(object):

    def __init__(self, lx=None, ly=None, ly_err=None):
        """Initialises and calculates statistics as member variables.
        """

        if lx is None or ly is None:
            # Initialise empty
            self.w = None
            self.xm = None
            self.x2m = None
            self.ym = None
            self.xym = None
        else:
            # Calculate statistics

            if ly_err is None:
                ly_err = np.ones_like(lx)

            lw = ly_err ** -2

            # Calculate needed statistics
            self.w = lw.sum()
            self.xm = np.average(lx, weights=lw)
            self.x2m = np.average(lx**2, weights=lw)
            self.ym = np.average(ly, weights=lw)
            self.xym = np.average(lx * ly, weights=lw)

        return


class LinregressResults(object):

    def __init__(self, lstats=None):

        if lstats is None:

            # Initialise empty
            self.slope = None
            self.intercept = None
            self.slope_err = None
            self.intercept_err = None
            self.slope_intercept_covar

            return

        elif isinstance(lstats, list):

            # We have a list of stats, so combine them
            stats = self.combine_lstats(lstats)

        elif isinstance(lstats, LinregressStatistics):

            # Just calculate from this object
            stats = lstats

        dx2m = stats.x2m - stats.xm**2
        dxym = stats.xym - stats.xm * stats.ym

        self.slope = dxym / dx2m

        self.intercept = stats.ym - stats.xm * self.slope

        self.slope_err = np.sqrt(1. / (stats.w * dx2m))

        self.intercept_err = np.sqrt(
            (1.0 + stats.xm ** 2 / dx2m) / stats.w)

        self.slope_intercept_covar = -stats.xm / \
            (stats.w * dx2m)

    @classmethod
    def combine_lstats(cls, lstats):

        # Set up arrays for each value
        n = len(lstats)
        lw = np.zeroes(n, dtype=float)
        lxm = np.zeroes(n, dtype=float)
        lx2m = np.zeroes(n, dtype=float)
        lym = np.zeroes(n, dtype=float)
        lxym = np.zeroes(n, dtype=float)

        # Fill in each array
        for i in range(n):
            lw[i] = lstats[i].w
            lxm[i] = lstats[i].xm
            lx2m[i] = lstats[i].x2m
            lym[i] = lstats[i].lym
            lxym[i] = lstats[i].lxym

        # Fill in an output object with weighted sums
        stats = LinregressStatistics()
        stats.w = lw.sum()
        stats.xm = np.average(lxm, weights=lw)
        stats.x2m = np.average(lx2m, weights=lw)
        stats.ym = np.average(lym, weights=lw)
        stats.xym = np.average(lxym, weights=lw)

        return stats


def get_linregress_statistics(x, y, y_err=None):
    """Functional interface to get a linear regression statistics object.
    """

    return LinregressStatistics(x, y, y_err=None)


def linregress_with_errors(x, y, y_err=None):
    """
    @brief
        Perform a linear regression with errors on the y values
    @details
        This uses a direct translation of GSL's gsl_fit_wlinear function, using
        inverse-variance weighting

    @param x <np.ndarray>
    @param y <np.ndarray>
    @param y_err <np.ndarray>

    @return results <LinregressResults>
    """

    stats = LinregressStatistics(x, y, y_err)
    results = LinregressResults(stats)

    return results


def decompose_transformation_matrix(m):
    """Decomposes a translation-free 2x2 transformation matrix into a scale matrix and rotation matrix.

    Parameters
    ----------
    m : 2x2 np.matrix

    Returns
    -------
    s : 2x2 np.matrix
        Scale matrix
    r : 2x2 np.matrix
        Rotation matrix
    """

    s0 = np.sqrt(m[0, 0] ** 2 + m[1, 0] ** 2)
    s1 = np.sqrt(m[0, 1] ** 2 + m[1, 1] ** 2)

    s = np.matrix([[s0, 0],
                   [0, s1]])

    r = np.matrix([[m[0, 0] / s0, m[0, 1] / s1],
                   [m[1, 0] / s0, m[1, 1] / s1]])

    return s, r
