""" @file math.py

    Created 12 February, 2018

    Miscellaneous mathematical functions
"""

__updated__ = "2021-08-13"

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
from typing import Optional

import numpy as np

DEFAULT_M_TARGET = 1e-4
DEFAULT_C_TARGET = 5e-6


class LinregressStatistics():

    def __init__(self, lx = None, ly = None, ly_err = None):
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
                ly_err = np.ones_like(lx, dtype = float)

            lw = ly_err ** -2

            # Calculate needed statistics
            self.w = np.nansum(lw)

            # Catch for bad data
            if self.w <= 0:
                self.xm = 0
                self.x2m = 0
                self.ym = 0
                self.xym = 0
            else:
                self.xm = np.nansum(lx * lw) / self.w
                self.x2m = np.nansum(lx ** 2 * lw) / self.w
                self.ym = np.nansum(ly * lw) / self.w
                self.xym = np.nansum(lx * ly * lw) / self.w


class LinregressResults():
    # Attrs set at init
    _slope = None
    _slope_err = None
    _intercept = None
    _intercept_err = None
    _slope_intercept_covar = None

    # Attrs calculated and cached on-demand
    _slope_sigma = None
    _intercept_sigma = None

    @property
    def slope(self):
        return self._slope

    @slope.setter
    def slope(self, slope):
        self._slope = slope
        # Uncache slope_sigma
        self._slope_sigma = None

    @property
    def slope_err(self):
        return self._slope_err

    @slope_err.setter
    def slope_err(self, slope_err):
        self._slope_err = slope_err
        # Uncache slope_sigma
        self._slope_sigma = None

    @property
    def intercept(self):
        return self._intercept

    @intercept.setter
    def intercept(self, intercept):
        self._intercept = intercept
        # Uncache intercept_sigma
        self._intercept_sigma = None

    @property
    def intercept_err(self):
        return self._intercept_err

    @intercept_err.setter
    def intercept_err(self, intercept_err):
        self._intercept_err = intercept_err
        # Uncache intercept_sigma
        self._intercept_sigma = None

    @property
    def slope_intercept_covar(self):
        return self._slope_intercept_covar

    @slope_intercept_covar.setter
    def slope_intercept_covar(self, slope_intercept_covar):
        self._slope_intercept_covar = slope_intercept_covar

    # Getters for attrs calculated and cached on-demand

    @property
    def slope_sigma(self):

        # Calculate _slope_sigma if required
        if ((self._slope_sigma is None) and (self.slope is not None) and
                (self.slope_err is not None)):
            slope_diff = np.abs(self.slope)
            self._slope_sigma = slope_diff / self.slope_err

        return self._slope_sigma

    @property
    def intercept_sigma(self):

        # Calculate _intercept_sigma if required
        if ((self._intercept_sigma is None) and (self.intercept is not None) and
                (self.intercept_err is not None)):
            intercept_diff = np.abs(self.intercept)
            self._intercept_sigma = intercept_diff / self.intercept_err

        return self._intercept_sigma

    def __init__(self, lstats = None):

        if lstats is None:

            # Initialise empty
            self.slope = None
            self.intercept = None
            self.slope_err = None
            self.intercept_err = None
            self.slope_intercept_covar = None

            return

        if isinstance(lstats, (list, np.ndarray)):

            # We have a list of stats, so combine them
            stats = self.combine_lstats(lstats)

        elif isinstance(lstats, LinregressStatistics):

            # Just calculate from this object
            stats = lstats

        dx2m = stats.x2m - stats.xm ** 2
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
        lw = np.zeros(n, dtype = float)
        lxm = np.zeros(n, dtype = float)
        lx2m = np.zeros(n, dtype = float)
        lym = np.zeros(n, dtype = float)
        lxym = np.zeros(n, dtype = float)

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


class BiasMeasurements():
    """Class for expressing bias measurements. Similar to LinregressResults
       except in terms of m and c.
    """

    # Attrs set at init
    _m = None
    _m_err = None
    _m_target = DEFAULT_M_TARGET
    _c = None
    _c_err = None
    _c_target = DEFAULT_C_TARGET
    _mc_covar = None

    # Attrs calculated and cached on-demand
    _m_sigma = None
    _c_sigma = None

    def __init__(self, linregress_results = None, m = 0., m_err = 0., c = 0., c_err = 0., mc_covar = 0.):

        if linregress_results is not None:
            # Init from linregress results
            if linregress_results.slope is None:
                self.m = None
            else:
                self.m = linregress_results.slope - 1
            self.m_err = linregress_results.slope_err
            self.c = linregress_results.intercept
            self.c_err = linregress_results.intercept_err
            self.mc_covar = linregress_results.slope_intercept_covar
        else:
            # Init from values
            self.m = m
            self.m_err = m_err
            self.c = c
            self.c_err = c_err
            self.mc_covar = mc_covar

    # Getters and setters for attrs set at init

    @property
    def m(self):
        return self._m

    @m.setter
    def m(self, m):
        self._m = m
        # Uncache m_sigma
        self._m_sigma = None

    @property
    def m_err(self):
        return self._m_err

    @m_err.setter
    def m_err(self, m_err):
        self._m_err = m_err
        # Uncache m_sigma
        self._m_sigma = None

    @property
    def m_target(self):
        return self._m_target

    @m_target.setter
    def m_target(self, m_target):
        self._m_target = m_target
        # Uncache m_sigma
        self._m_sigma = None

    @property
    def c(self):
        return self._c

    @c.setter
    def c(self, c):
        self._c = c
        # Uncache c_sigma
        self._c_sigma = None

    @property
    def c_err(self):
        return self._c_err

    @c_err.setter
    def c_err(self, c_err):
        self._c_err = c_err
        # Uncache c_sigma
        self._c_sigma = None

    @property
    def c_target(self):
        return self._c_target

    @c_target.setter
    def c_target(self, c_target):
        self._c_target = c_target
        # Uncache c_sigma
        self._c_sigma = None

    @property
    def mc_covar(self):
        return self._mc_covar

    @mc_covar.setter
    def mc_covar(self, mc_covar):
        self._mc_covar = mc_covar

    # Getters for attrs calculated and cached on-demand

    @property
    def m_sigma(self):

        # Calculate _m_sigma if required
        if ((self._m_sigma is None) and (self.m is not None) and
                (self.m_err is not None) and (self.m_target is not None)):
            m_diff = np.abs(self.m) - np.abs(self.m_target)
            self._m_sigma = np.where(m_diff > 0, m_diff / self.m_err, 0.)

        return self._m_sigma

    @property
    def c_sigma(self):

        # Calculate _c_sigma if required
        if ((self._c_sigma is None) and (self.c is not None) and
                (self.c_err is not None) and (self.c_target is not None)):
            c_diff = np.abs(self.c) - np.abs(self.c_target)
            self._c_sigma = np.where(c_diff > 0, c_diff / self.c_err, 0.)

        return self._c_sigma


def get_linregress_statistics(lx, ly, ly_err = None):
    """Functional interface to get a linear regression statistics object.
    """

    return LinregressStatistics(lx = lx, ly = ly, ly_err = ly_err)


def combine_linregress_statistics(lstats):
    """Functional interface to combine linear regression statistics objects
       into the result of a regression.
    """

    return LinregressResults(lstats = lstats)


DEFAULT_N_BOOTSTRAP_SAMPLES = 50
DEFAULT_BOOTSTRAP_SEED = 4612412


def linregress_with_errors(x: np.ndarray,
                           y: np.ndarray,
                           y_err: Optional[np.ndarray] = None,
                           bootstrap: bool = False,
                           n_bootstrap_samples: int = DEFAULT_N_BOOTSTRAP_SAMPLES,
                           bootstrap_seed: int = DEFAULT_BOOTSTRAP_SEED) -> LinregressResults:
    """ Perform a linear regression with errors on the y values. This forwards to the appropriate function depending on
        whether or not bootstrap error calculation is requested - either linregress_with_errors_no_bootstrap if
        bootstrap==False or else linregress_with_errors_bootstrap if bootstrap==True. If y_err is provided and
        bootstrap==False, all errors should be correct and independent, or else the resulting slope and intercept
        errors will be incorrect.

        Parameters
        ----------
        x : np.ndarray
        y : np.ndarray
        y_err : Optional[np.ndarray], default None
        bootstrap: bool, default False
            Whether or not slope and intercept errors should be calculated with a bootstrap approach. If all errors
            provided to y_err are trusted to be correct and independent, then this should be left as False for faster
            and more accurate error calculation. If this is not the case and accurate slope and intercept errors are
            desired, this should be set to true, with n_bootstrap_samples set to balance time and accuracy requirements.
        n_bootstrap_samples: int, default DEFAULT_N_BOOTSTRAP_SAMPLES
            If bootstrap==True, this will be the number of bootstrap samples used to calculate slope and intercept
            errors. Execution time will scale as n_bootstrap_samples, and precision as 1/sqrt(n_bootstrap_samples)
        bootstrap_seed: int, default DEFAULT_BOOTSTRAP_SEED
            If bootstrap==True, this will be the RNG seed used for the generation of bootstrap samples.

        Returns
        -------
        results : LinregressResults
    """

    if bootstrap:
        return linregress_with_errors_bootstrap(x = x,
                                                y = y,
                                                y_err = y_err,
                                                n_bootstrap_samples = n_bootstrap_samples,
                                                bootstrap_seed = bootstrap_seed)
    else:
        return linregress_with_errors_no_bootstrap(x = x,
                                                   y = y,
                                                   y_err = y_err)


def linregress_with_errors_no_bootstrap(x: np.ndarray,
                                        y: np.ndarray,
                                        y_err: Optional[np.ndarray] = None) -> LinregressResults:
    """ Perform a linear regression with errors on the y values. In order for the resulting slope and intercept errors
        to be correct, this implementation requires that, if y_err is provided, all errors are accurate and independent.

        Parameters
        ----------
        x : np.ndarray
        y : np.ndarray
        y_err : Optional[np.ndarray], default None

        Returns
        -------
        results : LinregressResults
    """

    stats = LinregressStatistics(x, y, y_err)
    results = LinregressResults(stats)

    return results


def decompose_transformation_matrix(m):
    """Decomposes a translation-free 2x2 transformation matrix into a scale matrix and rotation matrix.

    Parameters
    ----------
    m : 2x2 np.array

    Returns
    -------
    s : 2x2 np.array
        Scale matrix
    r : 2x2 np.array
        Rotation matrix
    """

    s0 = np.sqrt(m[0, 0] ** 2 + m[1, 0] ** 2)
    s1 = np.sqrt(m[0, 1] ** 2 + m[1, 1] ** 2)

    s = np.array([[s0, 0],
                  [0, s1]])

    r = np.array([[m[0, 0] / s0, m[0, 1] / s1],
                  [m[1, 0] / s0, m[1, 1] / s1]])

    return s, r
