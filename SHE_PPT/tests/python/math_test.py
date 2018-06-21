""" @file math_test.py

    Created 21 June 2017

    Tests of functions in the 'math' module.
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

import logging
from numpy.testing import assert_almost_equal
import os
from scipy.stats import linregress

import pytest

from SHE_PPT.math import linregress_with_errors
import numpy as np


class Test_math():

    def test_linregress_with_errors_simple(self):
        """Unit test of linregress_with_errors.
        """

        # Some test input
        x = np.array([1, 2, 4, 8, 7])
        y = np.array([10, 11,  9,  7, 12])
        y_err = np.array([0.1, 0.2, 0.1, 0.2, 0.4])

        # Calculate the regression
        weighted_results = linregress_with_errors(x, y, y_err)

        # Test they match expectations
        assert_almost_equal(weighted_results.slope, -0.34995112414467133)
        assert_almost_equal(weighted_results.intercept, 10.54740957966764)
        assert_almost_equal(weighted_results.slope_err, 0.028311906106274067)
        assert_almost_equal(weighted_results.intercept_err, 0.1076724332578932)
        assert_almost_equal(
            weighted_results.slope_intercept_covar, -0.0024828934506353857)

        # Test it matches results for regular regression if we don't use
        # weights
        unweighted_results = linregress_with_errors(x, y)
        slope, intercept, _, _, _ = linregress(x, y)

        assert_almost_equal(unweighted_results.slope, slope)
        assert_almost_equal(unweighted_results.intercept, intercept)

    def test_linregress_with_errors_full(self):
        """Unit test of linregress_with_errors that does a full simulation
           to test results.
        """

        # Set up test input

        ex_slope = 0.3
        ex_intercept = 10.2
        n = 10
        n_test = 1000

        x = np.linspace(0, n - 1, num=n, endpoint=True, dtype=float)
        base_y = ex_intercept + ex_slope * x

        np.random.seed(1234)

        y_err = np.random.random(n)

        # Run a set of tests
        slopes = np.zeros(n_test)
        intercepts = np.zeros(n_test)
        slope_errs = np.zeros(n_test)
        intercept_errs = np.zeros(n_test)
        slope_intercept_covars = np.zeros(n_test)

        for i in range(n_test):
            yz = np.random.randn(n)
            y = base_y + y_err * yz

            regress_results = linregress_with_errors(x, y, y_err)

            slopes[i] = regress_results.slope
            intercepts[i] = regress_results.intercept
            slope_errs[i] = regress_results.slope_err
            intercept_errs[i] = regress_results.intercept_err
            slope_intercept_covars[i] = regress_results.slope_intercept_covar

        # Get mean results
        slope_mean = np.mean(slopes)
        slope_std = np.std(slopes)
        intercept_mean = np.mean(intercepts)
        intercept_std = np.std(intercepts)

        # Check the results are reasonable
        assert_almost_equal(slope_mean, ex_slope, decimal=2)
        assert_almost_equal(intercept_mean, ex_intercept, decimal=2)
        assert_almost_equal(slope_std, np.mean(slope_errs), decimal=2)
        assert_almost_equal(intercept_std, np.mean(intercept_errs), decimal=2)

        # TODO check covar
