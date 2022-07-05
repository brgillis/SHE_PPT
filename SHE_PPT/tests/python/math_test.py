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
from scipy.stats import linregress

from SHE_PPT.math import (BiasMeasurements, DEFAULT_BOOTSTRAP_SEED, LinregressResults,
                          combine_linregress_statistics, get_linregress_statistics,
                          linregress_with_errors_bootstrap,
                          linregress_with_errors_no_bootstrap, )
from SHE_PPT.testing.utility import SheTestCase


class TestMath(SheTestCase):

    def setup_test_data(self):

        # Set up test input

        self.ex_slope = 0.3
        self.ex_intercept = 4.7
        self.y_err_mag = 0.1
        self.n_test_points = 10
        self.n_tests = 1000

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
        assert np.isclose(weighted_results.slope, -0.34995112414467133)
        assert np.isclose(weighted_results.intercept, 10.54740957966764)
        assert np.isclose(weighted_results.slope_err, 0.028311906106274067)
        assert np.isclose(weighted_results.intercept_err, 0.1076724332578932)
        assert np.isclose(
            weighted_results.slope_intercept_covar, -0.0024828934506353857)

        # Test it matches results for regular regression if we don't use
        # weights
        unweighted_results = linregress_with_errors_no_bootstrap(x, y)
        slope, intercept, _, _, _ = linregress(x, y)

        assert np.isclose(unweighted_results.slope, slope)
        assert np.isclose(unweighted_results.intercept, intercept)

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

        rtol = 0.1
        atol = 0.001

        def assert_close(a: float, b: float) -> None:
            """ Conveniece function to check values are close with our chosen tolerances.
            """
            assert np.isclose(a, b, rtol = rtol, atol = atol)

        # Set up some things differently depending on whether we're bootstrapping or not
        if not bootstrap:
            linregress_function = linregress_with_errors_no_bootstrap
            kwargs = {}
        else:
            linregress_function = linregress_with_errors_bootstrap
            n_bootstrap_samples = 100
            self.n_tests = self.n_tests // 10
            kwargs = {"bootstrap_seed"     : DEFAULT_BOOTSTRAP_SEED,
                      "n_bootstrap_samples": n_bootstrap_samples}

        x = np.linspace(0, 100, num = self.n_test_points, endpoint = True, dtype = float)
        base_y = self.ex_intercept + self.ex_slope * x

        rng = np.random.default_rng(1234)

        y_err = self.y_err_mag * (0.5 + rng.uniform(size = self.n_test_points))

        # Run a set of tests
        slopes = np.zeros(self.n_tests)
        intercepts = np.zeros(self.n_tests)
        slope_errs = np.zeros(self.n_tests)
        intercept_errs = np.zeros(self.n_tests)
        slope_intercept_covars = np.zeros(self.n_tests)
        lstats = []

        for i in range(self.n_tests):
            yz = rng.normal(size = self.n_test_points)
            y = base_y + y_err * yz

            if bootstrap:
                # Use a different bootstrap seed each time
                kwargs["bootstrap_seed"] += 1

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

        assert_close(slope_mean, self.ex_slope)
        assert_close(intercept_mean, self.ex_intercept)
        assert_close(slope_std, np.mean(slope_errs))
        assert_close(intercept_std, np.mean(intercept_errs))
        assert_close(slope_intercept_cov, np.mean(slope_intercept_covars))

        # Now check if it works the same by compiling statistics
        combined_results = combine_linregress_statistics(lstats)
        assert_close(combined_results.slope, self.ex_slope)
        assert_close(combined_results.intercept, self.ex_intercept)
        assert_close(combined_results.slope_err, np.mean(slope_errs) / np.sqrt(self.n_tests))
        assert_close(combined_results.intercept_err, np.mean(intercept_errs) / np.sqrt(self.n_tests))
        assert_close(combined_results.slope_intercept_covar, np.mean(slope_intercept_covars))

    def test_linregress_with_errors_bootstrap_corr_errors(self):
        """ Tests bootstrap error calculation in the case of correlated errors.
        """

        id = np.arange(self.n_test_points)
        x = np.linspace(0, 100, num = self.n_test_points, endpoint = True, dtype = float)
        base_y = self.ex_intercept + self.ex_slope * x

        rng = np.random.default_rng(1234)

        y_err = self.y_err_mag * (0.5 + rng.uniform(size = self.n_test_points))
        yz = rng.normal(size = self.n_test_points)
        y = base_y + y_err * yz

        def duplicate_data(a: np.ndarray, times: int) -> np.ndarray:
            a_out = a
            for i in range(times - 1):
                a_out = np.concatenate([a_out, a])
            return a_out

        # Get the base results first
        base_results = linregress_with_errors_bootstrap(x, y, y_err = y_err, id = id)

        # Not get results with duplicated data
        n_duplicates = 4
        id_dup = duplicate_data(id, n_duplicates)
        x_dup = duplicate_data(x, n_duplicates)
        y_dup = duplicate_data(y, n_duplicates)
        y_err_dup = duplicate_data(y_err, n_duplicates)

        dup_results = linregress_with_errors_bootstrap(x_dup, y_dup, y_err_dup, id = id_dup)

        # Check slope, intercept, and errors are all about the same
        assert np.isclose(base_results.slope, dup_results.slope, rtol = 0.1)
        assert np.isclose(base_results.slope_err, dup_results.slope_err, rtol = 0.1)
        assert np.isclose(base_results.intercept, dup_results.intercept, rtol = 0.1)
        assert np.isclose(base_results.intercept_err, dup_results.intercept_err, rtol = 0.1)

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
