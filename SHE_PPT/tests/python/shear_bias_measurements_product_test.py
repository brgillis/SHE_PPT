""" @file shear_estimates_product_test.py

    Created 9 Oct 2017

    Unit tests for the shear estimates data product.
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

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.math import linregress_with_errors, BiasMeasurements
from SHE_PPT.products import shear_bias_measurements as prod
import numpy as np


class TestShearBiasMeasurementsProduct(object):
    """A collection of tests for the shear bias measurements data product.

    """

    def test_validation(self):

        prod.init()

        n = 10

        measurements = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            measurements[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                    BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

        # Create the product
        product = prod.create_dpd_shear_bias_measurements(BFD_g1_bias_measurements=measurements["BFD"][0],
                                                          BFD_g2_bias_measurements=measurements[
                                                              "BFD"][1],
                                                          KSB_g1_bias_measurements=measurements[
                                                              "KSB"][0],
                                                          KSB_g2_bias_measurements=measurements[
                                                              "KSB"][1],
                                                          LensMC_g1_bias_measurements=measurements[
                                                              "LensMC"][0],
                                                          LensMC_g2_bias_measurements=measurements[
                                                              "LensMC"][1],
                                                          MomentsML_g1_bias_measurements=measurements[
                                                              "MomentsML"][0],
                                                          MomentsML_g2_bias_measurements=measurements[
                                                              "MomentsML"][1],
                                                          REGAUSS_g1_bias_measurements=measurements[
                                                              "REGAUSS"][0],
                                                          REGAUSS_g2_bias_measurements=measurements["REGAUSS"][1])

        # Check that it validates the schema
        product.validateBinding()

        # Check that it was inited with the proper values
        assert product.get_BFD_bias_measurements() == measurements["BFD"]
        assert product.get_KSB_bias_measurements() == measurements["KSB"]
        assert product.get_LensMC_bias_measurements() == measurements["LensMC"]
        assert product.get_MomentsML_bias_measurements() == measurements["MomentsML"]
        assert product.get_REGAUSS_bias_measurements() == measurements["REGAUSS"]

        # Check the general get method works
        measurements2 = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            assert product.get_method_bias_measurements(
                method) == measurements[method]

            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            measurements2[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                     BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

            product.set_method_bias_measurements(method, *stats2[method])
            assert product.get_method_bias_measurements(
                method) == stats2[method]

        pass

    def test_xml_writing_and_reading(self, tmpdir):

        prod.init()

        n = 10

        # Create the product
        product = prod.create_dpd_shear_bias_measurements()

        measurements = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            measurements[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                    BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

        # Create the product
        product = prod.create_dpd_shear_bias_measurements(BFD_g1_bias_measurements=measurements["BFD"][0],
                                                          BFD_g2_bias_measurements=measurements[
                                                              "BFD"][1],
                                                          KSB_g1_bias_measurements=measurements[
                                                              "KSB"][0],
                                                          KSB_g2_bias_measurements=measurements[
                                                              "KSB"][1],
                                                          LensMC_g1_bias_measurements=measurements[
                                                              "LensMC"][0],
                                                          LensMC_g2_bias_measurements=measurements[
                                                              "LensMC"][1],
                                                          MomentsML_g1_bias_measurements=measurements[
                                                              "MomentsML"][0],
                                                          MomentsML_g2_bias_measurements=measurements[
                                                              "MomentsML"][1],
                                                          REGAUSS_g1_bias_measurements=measurements[
                                                              "REGAUSS"][0],
                                                          REGAUSS_g2_bias_measurements=measurements["REGAUSS"][1])

        # Save the product in an XML file
        filename = tmpdir.join("she_shear_estimates.xml")
        write_xml_product(product, filename)

        # Read back the XML file
        loaded_product = read_xml_product(filename)

        # Check that the products coincide
        assert loaded_product.get_BFD_bias_measurements()[0].m == measurements["BFD"][0].m
        assert loaded_product.get_BFD_bias_measurements()[1].m == measurements["BFD"][1].m
        assert loaded_product.get_KSB_bias_measurements()[0].m == measurements["KSB"][0].m
        assert loaded_product.get_KSB_bias_measurements()[1].m == measurements["KSB"][1].m
        assert loaded_product.get_LensMC_bias_measurements()[0].m == measurements["LensMC"][0].m
        assert loaded_product.get_LensMC_bias_measurements()[1].m == measurements["LensMC"][1].m
        assert loaded_product.get_MomentsML_bias_measurements(
        )[0].m == measurements["MomentsML"][0].m
        assert loaded_product.get_MomentsML_bias_measurements(
        )[1].m == measurements["MomentsML"][1].m
        assert loaded_product.get_REGAUSS_bias_measurements()[0].m == measurements["REGAUSS"][0].m
        assert loaded_product.get_REGAUSS_bias_measurements()[1].m == measurements["REGAUSS"][1].m

        return
