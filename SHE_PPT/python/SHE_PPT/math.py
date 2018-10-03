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
                ly_err = np.ones_like(lx, dtype=float)

            lw = ly_err ** -2

            # Calculate needed statistics
            self.w = lw.sum()

            # Catch for bad data
            if self.w <= 0:
                self.xm = 0
                self.x2m = 0
                self.ym = 0
                self.xym = 0
            else:
                self.xm = np.nansum(lx * lw) / self.w
                self.x2m = np.nansum(lx**2 * lw) / self.w
                self.ym = np.nansum(ly * lw) / self.w
                self.xym = np.nansum(lx * ly * lw) / self.w

        return


class LinregressResults(object):

    def __init__(self, lstats=None):

        if lstats is None:

            # Initialise empty
            self.slope = None
            self.intercept = None
            self.slope_err = None
            self.intercept_err = None
            self.slope_intercept_covar = None

            return

        elif isinstance(lstats, list) or isinstance(lstats, np.ndarray):

            # We have a list of stats, so combine them
            stats = self.combine_lstats(lstats)

        elif isinstance(lstats, LinregressStatistics):

            # Just calculate from this object
            stats = lstats

        dx2m = stats.x2m - stats.xm**2
        dxym = stats.xym - stats.xm * stats.ym

        if dx2m <= 0:
            self.slope = np.inf
            self.intercept = np.nan
        else:
            self.slope = dxym / dx2m
            self.intercept = stats.ym - stats.xm * self.slope

        if dx2m <= 0 or stats.w == 0:
            self.slope_err = np.inf
            self.intercept_err = np.nan
            self.slope_intercept_covar = np.nan
        else:
            self.slope_err = np.sqrt(1. / (stats.w * dx2m))
            self.intercept_err = np.sqrt((1.0 + stats.xm ** 2 / dx2m) / stats.w)
            self.slope_intercept_covar = -stats.xm / (stats.w * dx2m)

    @classmethod
    def combine_lstats(cls, lstats):

        # Set up arrays for each value
        n = len(lstats)
        lw = np.zeros(n, dtype=float)
        lxm = np.zeros(n, dtype=float)
        lx2m = np.zeros(n, dtype=float)
        lym = np.zeros(n, dtype=float)
        lxym = np.zeros(n, dtype=float)

        # Fill in each array
        for i in range(n):
            lw[i] = lstats[i].w
            lxm[i] = lstats[i].xm
            lx2m[i] = lstats[i].x2m
            lym[i] = lstats[i].ym
            lxym[i] = lstats[i].xym

        # Fill in an output object with weighted sums
        stats = LinregressStatistics()
        stats.w = lw.sum()
        stats.xm = np.nansum(lxm * lw) / lw.sum()
        stats.x2m = np.nansum(lx2m * lw) / lw.sum()
        stats.ym = np.nansum(lym * lw) / lw.sum()
        stats.xym = np.nansum(lxym * lw) / lw.sum()

        return stats


class BiasMeasurements(object):
    """Class for expressing bias measurements. Similar to LinregressResults
       except in terms of m and c.
    """

    def __init__(self, linregress_results=None):

        if linregress_results is None:
            self.m = None
            self.m_err = None
            self.c = None
            self.c_err = None
            self.mc_covar = None
        else:
            self.m = linregress_results.slope - 1
            self.m_err = linregress_results.slope_err
            self.c = linregress_results.intercept
            self.c_err = linregress_results.intercept_err
            self.mc_covar = linregress_results.slope_intercept_covar

        return


def get_linregress_statistics(lx, ly, ly_err=None):
    """Functional interface to get a linear regression statistics object.
    """

    return LinregressStatistics(lx=lx, ly=ly, ly_err=ly_err)


def combine_linregress_statistics(lstats):
    """Functional interface to combine linear regression statistics objects
       into the result of a regression.
    """

    return LinregressResults(lstats=lstats)


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
