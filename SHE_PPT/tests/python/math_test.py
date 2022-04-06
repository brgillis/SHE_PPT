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

__updated__ = "2021-07-05"

import numpy as np
from numpy.testing import assert_almost_equal
from scipy.stats import linregress

from SHE_PPT.math import (BiasMeasurements, DEFAULT_BOOTSTRAP_SEED, DEFAULT_N_BOOTSTRAP_SAMPLES, LinregressResults,
                          combine_linregress_statistics, get_linregress_statistics,
                          linregress_with_errors_bootstrap,
                          linregress_with_errors_no_bootstrap, )


class Test_math():

    def test_linregress_with_errors_simple(self):
        """Unit test of linregress_with_errors.
        """

        # Some test input
        x = np.array([1, 2, 4, 8, 7])
        y = np.array([10, 11, 9, 7, 12])
        y_err = np.array([0.1, 0.2, 0.1, 0.2, 0.4])

        # Calculate the regression
        weighted_results = linregress_with_errors_no_bootstrap(x, y, y_err)

        # Test they match expectations
        assert_almost_equal(weighted_results.slope, -0.34995112414467133)
        assert_almost_equal(weighted_results.intercept, 10.54740957966764)
        assert_almost_equal(weighted_results.slope_err, 0.028311906106274067)
        assert_almost_equal(weighted_results.intercept_err, 0.1076724332578932)
        assert_almost_equal(
            weighted_results.slope_intercept_covar, -0.0024828934506353857)

        # Test it matches results for regular regression if we don't use
        # weights
        unweighted_results = linregress_with_errors_no_bootstrap(x, y)
        slope, intercept, _, _, _ = linregress(x, y)

        assert_almost_equal(unweighted_results.slope, slope)
        assert_almost_equal(unweighted_results.intercept, intercept)

    def test_linregress_with_errors_full_no_bootstrap(self):
        """Unit test of linregress_with_errors that does a full simulation
           to test results, for a non-bootstrap approach.
        """

        self._test_linregress_with_errors_full(bootstrap = False)

    def test_linregress_with_errors_full_bootstrap(self):
        """Unit test of linregress_with_errors that does a full simulation
           to test results, for a bootstrap approach.
        """

        self._test_linregress_with_errors_full(bootstrap = True)

    def _test_linregress_with_errors_full(self, bootstrap: bool):
        """Unit test of linregress_with_errors that does a full simulation
           to test results - for either bootstrap or non-bootstrap approach.
        """

        if not bootstrap:
            linregress_function = linregress_with_errors_no_bootstrap
        else:
            linregress_function = linregress_with_errors_bootstrap

        # Set up test input

        ex_slope = 0.3
        ex_intercept = 10.2
        n = 10
        n_test = 1000
        if bootstrap:
            n_test = n_test // DEFAULT_N_BOOTSTRAP_SAMPLES

        x = np.linspace(0, n - 1, num = n, endpoint = True, dtype = float)
        base_y = ex_intercept + ex_slope * x

        np.random.seed(1234)

        y_err = np.random.random(n)

        # Run a set of tests
        slopes = np.zeros(n_test)
        intercepts = np.zeros(n_test)
        slope_errs = np.zeros(n_test)
        intercept_errs = np.zeros(n_test)
        slope_intercept_covars = np.zeros(n_test)
        lstats = []

        for i in range(n_test):
            yz = np.random.randn(n)
            y = base_y + y_err * yz

            if bootstrap:
                kwargs = {"bootstrap_seed": DEFAULT_BOOTSTRAP_SEED + i}
            else:
                kwargs = {}

            # Get and save the regression results for this run
            regress_results = linregress_function(x, y, y_err, **kwargs)

            slopes[i] = regress_results.slope
            intercepts[i] = regress_results.intercept
            slope_errs[i] = regress_results.slope_err
            intercept_errs[i] = regress_results.intercept_err
            slope_intercept_covars[i] = regress_results.slope_intercept_covar

            # Also save statistics to test that that works
            lstats.append(get_linregress_statistics(x, y, y_err))

        # Get mean results
        slope_mean = np.mean(slopes)
        slope_std = np.std(slopes)
        intercept_mean = np.mean(intercepts)
        intercept_std = np.std(intercepts)
        slope_intercept_cov = np.cov(slopes, intercepts)[0, 1]

        # Check the results are reasonable

        if bootstrap:
            # Use more relaxed checking in the bootstrap case due to the smaller number of samples
            decimal = 1
        else:
            decimal = 2

        assert_almost_equal(slope_mean, ex_slope, decimal = decimal)
        assert_almost_equal(intercept_mean, ex_intercept, decimal = decimal)
        assert_almost_equal(slope_std, np.mean(slope_errs), decimal = decimal)
        assert_almost_equal(intercept_std, np.mean(intercept_errs), decimal = decimal)
        assert_almost_equal(
            slope_intercept_cov, np.mean(slope_intercept_covars), decimal = decimal)

        # Now check if it works the same by compiling statistics
        combined_results = combine_linregress_statistics(lstats)
        assert_almost_equal(combined_results.slope, ex_slope, decimal = decimal)
        assert_almost_equal(
            combined_results.intercept, ex_intercept, decimal = decimal)
        assert_almost_equal(
            combined_results.slope_err, np.mean(slope_errs) / np.sqrt(n_test), decimal = decimal)
        assert_almost_equal(
            combined_results.intercept_err, np.mean(intercept_errs) / np.sqrt(n_test), decimal = decimal)
        assert_almost_equal(
            combined_results.slope_intercept_covar, np.mean(slope_intercept_covars), decimal = decimal)

    def test_bias_measurement(self):

        # Set up the input for the test
        input_linregress_results = LinregressResults()

        input_linregress_results.slope = 1.5
        input_linregress_results.slope_err = 0.1
        input_linregress_results.intercept = -0.3
        input_linregress_results.intercept_err = 0.01
        input_linregress_results.slope_intercept_covar = 0.03

        bias_measurements = BiasMeasurements(input_linregress_results)

        # Test everything is initialized properly
        assert np.isclose(bias_measurements.m, input_linregress_results.slope - 1)
        assert np.isclose(bias_measurements.m_err, input_linregress_results.slope_err)
        assert np.isclose(bias_measurements.c, input_linregress_results.intercept)
        assert np.isclose(bias_measurements.c_err, input_linregress_results.intercept_err)
        assert np.isclose(bias_measurements.mc_covar, input_linregress_results.slope_intercept_covar)

        # Test sigma calculations
        bias_measurements.m_target = 0.1
        bias_measurements.c_target = 0.01

        assert np.isclose(bias_measurements.m_sigma, (bias_measurements.m -
                                                      bias_measurements.m_target) / bias_measurements.m_err)
        assert np.isclose(bias_measurements.c_sigma, -(bias_measurements.c -
                                                       -bias_measurements.c_target) / bias_measurements.c_err)
