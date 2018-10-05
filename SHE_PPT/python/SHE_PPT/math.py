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
            if self.w <= 0:  # Catch for bad data
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

        elif isinstance(lstats, list) or isinstance(lstats,np.ndarray):

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

class BFDSumStatistics(object):

    def __init__(self, sums=None):
        """Initialises and calculates statistics as member variables.
        """

        if sums is None:
            # Initialise empty
            self.b1 = None
            self.b2 = None
            self.b3 = None
            self.b4 = None
            self.A11 = None
            self.A12 = None
            self.A13 = None
            self.A14 = None
            self.A22 = None
            self.A23 = None
            self.A24 = None
            self.A33 = None
            self.A34 = None
            self.A44 = None
        else:
            # Calculate statistics
            self.b1 = sums['b1']
            self.b2 = sums['b2']
            self.b3 = sums['b3']
            self.b4 = sums['b4']
            self.A11 = sums['A11']
            self.A12 = sums['A12']
            self.A13 = sums['A13']
            self.A14 = sums['A14']
            self.A22 = sums['A22']
            self.A23 = sums['A23']
            self.A24 = sums['A24']
            self.A33 = sums['A33']
            self.A34 = sums['A34']
            self.A44 = sums['A44']

 
        return
    
class BFDSumResults(object):

    def __init__(self, lstats=None,do_g1=True):

        if (lstats is None) or (lstats[0] is None):

            # Initialise empty
            self.slope = None
            self.intercept = None
            self.slope_err = None
            self.intercept_err = None
            self.slope_intercept_covar = None

            return

        elif isinstance(lstats, list):
            
            # We have a list of stats, so combine them
            stats = self.combine_lstats(lstats)

        elif isinstance(lstats, BFDSumStatistics):

            # Just calculate from this object
            stats = lstats

        C = np.matrix([[stats.A11,stats.A12,stats.A13,stats.A14],
                       [stats.A12,stats.A22,stats.A23,stats.A24],
                       [stats.A13,stats.A23,stats.A33,stats.A34],
                       [stats.A14,stats.A24,stats.A34,stats.A44]])
        Cinv=np.linalg.inv(C)
        Q_P=np.matrix([[stats.b1],[stats.b2],[stats.b3],[stats.b4]])

        if do_g1 == True:
            self.slope=(Cinv*Q_P)[0,0]
            self.intercept=(Cinv*Q_P)[1,0]
            self.slope_err=(np.sqrt(Cinv[0,0]))
            self.intercept_err=np.sqrt(Cinv[1,1])
            self.slope_intercept_covar=Cinv[0,1]
        else:
            self.slope=(Cinv*Q_P)[2,0]
            self.intercept=(Cinv*Q_P)[3,0]
            self.slope_err=(np.sqrt(Cinv[2,2]))
            self.intercept_err=np.sqrt(Cinv[3,3])
            self.slope_intercept_covar=Cinv[2,3]


    @classmethod
    def combine_lstats(cls, lstats):

        # Set up arrays for each value
        n = len(lstats)
         
       # Fill in an output object with weighted sums
        stats = BFDSumStatistics()
        stats.b1 = 0.
        stats.b2 = 0.
        stats.b3 = 0.
        stats.b4 = 0.
        stats.A11 = 0.
        stats.A12 = 0.
        stats.A13 = 0.
        stats.A14 = 0.
        stats.A22 = 0.
        stats.A23 = 0.
        stats.A24 = 0.
        stats.A33 = 0.
        stats.A34 = 0.
        stats.A44 = 0.

        # Fill in each array
        for i in range(n):
            stats.b1 += lstats[i].b1
            stats.b2 += lstats[i].b2
            stats.b3 += lstats[i].b3
            stats.b4 += lstats[i].b4
            stats.A11 += lstats[i].A11
            stats.A12 += lstats[i].A12
            stats.A13 += lstats[i].A13
            stats.A14 += lstats[i].A14
            stats.A22 += lstats[i].A22
            stats.A23 += lstats[i].A23
            stats.A24 += lstats[i].A24
            stats.A33 += lstats[i].A33
            stats.A34 += lstats[i].A34
            stats.A44 += lstats[i].A44

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

def get_bfd_sum_statistics(sums):
    """Functional interface to get a BFD Sum statistics object.
    """

    return BFDSumStatistics(sums=sums)


def combine_linregress_statistics(lstats):
    """Functional interface to combine linear regression statistics objects
       into the result of a regression.
    """

    return LinregressResults(lstats=lstats)

def combine_bfd_sum_statistics(lstats,do_g1=True):
    """Functional interface to combine linear regression statistics objects
       into the result of a regression.
    """

    return BFDSumResults(lstats=lstats,do_g1=do_g1)

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
