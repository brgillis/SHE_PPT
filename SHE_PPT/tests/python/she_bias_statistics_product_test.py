""" @file she_bias_statistics_product_test.py

    Created 15 July 2019

    Unit tests for the shear bias statistics data product.
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

__updated__ = "2021-08-12"

import os

from astropy.table import Table
import pytest

import SHE_PPT
from SHE_PPT.constants.shear_estimation_methods import ShearEstimationMethods
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.math import LinregressStatistics, BiasMeasurements, linregress_with_errors
from SHE_PPT.products import she_bias_statistics as prod
from SHE_PPT.table_formats.she_bias_statistics import calculate_bias_measurements
import numpy as np


seed = 10245


class TestShearBiasStatsProduct(object):
    """A collection of tests for the shear bias statistics data product.

    """

    def test_validation(self, tmpdir):

        workdir = str(tmpdir)
        np.random.seed(seed)

        n = 10

        measurements = {}
        stats = {}
        for method in (ShearEstimationMethods.KSB,
                       ShearEstimationMethods.LENSMC,
                       ShearEstimationMethods.MOMENTSML,
                       ShearEstimationMethods.REGAUSS):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            stats[method] = (LinregressStatistics(x1, y1, y_err),
                             LinregressStatistics(x2, y2, y_err),)

            measurements[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                    BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

        # Create the product
        product = prod.create_dpd_she_bias_statistics_from_stats(KSB_bias_statistics=stats[ShearEstimationMethods.KSB],
                                                                 LensMC_bias_statistics=stats[ShearEstimationMethods.LENSMC],
                                                                 MomentsML_bias_statistics=stats[ShearEstimationMethods.MOMENTSML],
                                                                 REGAUSS_bias_statistics=stats[ShearEstimationMethods.REGAUSS],
                                                                 workdir=workdir)

        # Check that it validates the schema
        product.validateBinding()

        # Check that it was inited with the proper values

        # Check the other methods' statistics are correct
        for val in ("w", "xm", "x2m", "ym", "xym"):
            for new_object, original_object in ((product.get_KSB_bias_statistics(workdir=workdir), stats[ShearEstimationMethods.KSB]),
                                                (product.get_LensMC_bias_statistics(
                                                    workdir=workdir), stats[ShearEstimationMethods.LENSMC]),
                                                (product.get_MomentsML_bias_statistics(
                                                    workdir=workdir), stats[ShearEstimationMethods.MOMENTSML]),
                                                (product.get_REGAUSS_bias_statistics(workdir=workdir), stats[ShearEstimationMethods.REGAUSS])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))

        # Check that all the bias measurements are correct
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for new_object, original_object in ((product.get_KSB_bias_measurements(workdir=workdir), measurements[ShearEstimationMethods.KSB]),
                                                (product.get_LensMC_bias_measurements(
                                                    workdir=workdir), measurements[ShearEstimationMethods.LENSMC]),
                                                (product.get_MomentsML_bias_measurements(
                                                    workdir=workdir), measurements[ShearEstimationMethods.MOMENTSML]),
                                                (product.get_REGAUSS_bias_measurements(workdir=workdir), measurements[ShearEstimationMethods.REGAUSS])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))

        # Check the general get and set methods work
        stats2 = {}
        measurements2 = {}
        for method in (ShearEstimationMethods.KSB,
                       ShearEstimationMethods.LENSMC,
                       ShearEstimationMethods.MOMENTSML,
                       ShearEstimationMethods.REGAUSS):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            stats2[method] = (LinregressStatistics(x1, y1, y_err),
                              LinregressStatistics(x2, y2, y_err),)

            product.set_method_bias_statistics(method, stats2[method], workdir=workdir)

            measurements2[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                     BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

        for method in (ShearEstimationMethods.KSB, ShearEstimationMethods.LENSMC, ShearEstimationMethods.MOMENTSML, ShearEstimationMethods.REGAUSS):
            for val in ("w", "xm", "x2m", "ym", "xym"):
                for new_object, original_object in ((product.get_KSB_bias_statistics(workdir=workdir), stats2[ShearEstimationMethods.KSB]),
                                                    (product.get_LensMC_bias_statistics(
                                                        workdir=workdir), stats2[ShearEstimationMethods.LENSMC]),
                                                    (product.get_MomentsML_bias_statistics(
                                                        workdir=workdir), stats2[ShearEstimationMethods.MOMENTSML]),
                                                    (product.get_REGAUSS_bias_statistics(workdir=workdir), stats2[ShearEstimationMethods.REGAUSS])):

                    assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                    assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))

        # Check that all the updated bias measurements are correct
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for new_object, original_object in ((product.get_KSB_bias_measurements(workdir=workdir), measurements2[ShearEstimationMethods.KSB]),
                                                (product.get_LensMC_bias_measurements(
                                                    workdir=workdir), measurements2[ShearEstimationMethods.LENSMC]),
                                                (product.get_MomentsML_bias_measurements(
                                                    workdir=workdir), measurements2[ShearEstimationMethods.MOMENTSML]),
                                                (product.get_REGAUSS_bias_measurements(workdir=workdir), measurements2[ShearEstimationMethods.REGAUSS])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))

        # Check that all the calculated bias measurements are correct
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for filename, method in ((product.get_KSB_bias_statistics_filename(), ShearEstimationMethods.KSB),
                                     (product.get_LensMC_bias_statistics_filename(), ShearEstimationMethods.LENSMC),
                                     (product.get_MomentsML_bias_statistics_filename(), ShearEstimationMethods.MOMENTSML),
                                     (product.get_REGAUSS_bias_statistics_filename(), ShearEstimationMethods.REGAUSS)):

                table = Table.read(os.path.join(workdir, filename))

                new_object = calculate_bias_measurements(table, update=False)
                original_object = measurements2[method]

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val),
                                  rtol=1e-4, atol=1e-5), "Method: " + method
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val),
                                  rtol=1e-4, atol=1e-5), "Method: " + method

    def test_xml_writing_and_reading(self, tmpdir):

        workdir = str(tmpdir)

        n = 10

        # Create the product
        product = prod.create_dpd_she_bias_statistics()

        stats = {}
        for method in (ShearEstimationMethods.KSB,
                       ShearEstimationMethods.LENSMC,
                       ShearEstimationMethods.MOMENTSML,
                       ShearEstimationMethods.REGAUSS):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err
            stats[method] = (LinregressStatistics(x1, y1, y_err),
                             LinregressStatistics(x2, y2, y_err),)
        # Create the product
        product = prod.create_dpd_she_bias_statistics_from_stats(KSB_bias_statistics=stats[ShearEstimationMethods.KSB],
                                                                 LensMC_bias_statistics=stats[ShearEstimationMethods.LENSMC],
                                                                 MomentsML_bias_statistics=stats[ShearEstimationMethods.MOMENTSML],
                                                                 REGAUSS_bias_statistics=stats[ShearEstimationMethods.REGAUSS],
                                                                 workdir=workdir)

        # Save the product in an XML file
        filename = "she_shear_estimates.xml"
        write_xml_product(product, filename, workdir=workdir)

        # Read back the XML file
        loaded_product = read_xml_product(filename, workdir=workdir)

        # Check that the products coincide

        for val in ("w", "xm", "x2m", "ym", "xym"):
            for loaded_object, original_object in ((loaded_product.get_KSB_bias_statistics(workdir=workdir), stats[ShearEstimationMethods.KSB]),
                                                   (loaded_product.get_LensMC_bias_statistics(
                                                       workdir=workdir), stats[ShearEstimationMethods.LENSMC]),
                                                   (loaded_product.get_MomentsML_bias_statistics(
                                                       workdir=workdir), stats[ShearEstimationMethods.MOMENTSML]),
                                                   (loaded_product.get_REGAUSS_bias_statistics(workdir=workdir), stats[ShearEstimationMethods.REGAUSS])):

                assert np.isclose(getattr(loaded_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(loaded_object[1], val), getattr(original_object[1], val))

        return
