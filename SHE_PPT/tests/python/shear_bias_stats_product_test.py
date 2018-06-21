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
from SHE_PPT.math import LinregressStatistics
from SHE_PPT.products import shear_bias_stats as prod
import numpy as np


class TestShearEstimatesProduct(object):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):

        prod.init()

        n = 10

        stats = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.randn(n) * y_err
            y2 = x2 + np.randn(n) * y_err

            stats[method] = (LinregressStatistics(x1, y1, y_err),
                             LinregressStatistics(x2, y2, y_err),)

        # Create the product
        product = prod.create_dpd_shear_bias_statistics(BFD_g1_statistics=stats["BFD"][0],
                                                        BFD_g2_statistics=stats[
                                                            "BFD"][1],
                                                        KSB_g1_statistics=stats[
                                                            "KSB"][0],
                                                        KSB_g2_statistics=stats[
                                                            "KSB"][1],
                                                        LensMC_g1_statistics=stats[
                                                            "LensMC"][0],
                                                        LensMC_g2_statistics=stats[
                                                            "LensMC"][1],
                                                        MomentsML_g1_statistics=stats[
                                                            "MomentsML"][0],
                                                        MomentsML_g2_statistics=stats[
                                                            "MomentsML"][1],
                                                        REGAUSS_g1_statistics=stats[
                                                            "REGAUSS"][0],
                                                        REGAUSS_g2_statistics=stats["REGAUSS"][1])

        # Check that it validates the schema
        product.validateBinding()

        # Check that it was inited with the proper values
        assert product.get_BFD_statistics() == stats["BFD"]
        assert product.get_KSB_statistics() == stats["KSB"]
        assert product.get_LensMC_statistics() == stats["LensMC"]
        assert product.get_MomentsML_statistics() == stats["MomentsML"]
        assert product.get_REGAUSS_statistics() == stats["REGAUSS"]

        # Check the general get method works#
        stats2 = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            assert product.get_method_statistics(method) == stats[method]

            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.randn(n) * y_err
            y2 = x2 + np.randn(n) * y_err

            stats2[method] = (LinregressStatistics(x1, y1, y_err),
                              LinregressStatistics(x2, y2, y_err),)

            product.set_method_statistics(method, *stats2[method])
            assert product.get_method_statistics(method) == stats2[method]

        pass

    def test_xml_writing_and_reading(self, tmpdir):

        prod.init()

        # Create the product
        product = prod.create_dpd_shear_estimates()

        # Change the fits filenames
        b_filename = "test_file_b.fits"
        product.set_BFD_filename(b_filename)
        k_filename = "test_file_k.fits"
        product.set_KSB_filename(k_filename)
        l_filename = "test_file_l.fits"
        product.set_LensMC_filename(l_filename)
        m_filename = "test_file_m.fits"
        product.set_MomentsML_filename(m_filename)
        r_filename = "test_file_r.fits"
        product.set_REGAUSS_filename(r_filename)

        # Save the product in an XML file
        filename = tmpdir.join("she_shear_estimates.xml")
        write_xml_product(product, filename)

        # Read back the XML file
        loaded_product = read_xml_product(filename)

        # Check that the filenames coincide
        assert loaded_product.get_BFD_filename() == b_filename
        assert loaded_product.get_KSB_filename() == k_filename
        assert loaded_product.get_LensMC_filename() == l_filename
        assert loaded_product.get_MomentsML_filename() == m_filename
        assert loaded_product.get_REGAUSS_filename() == r_filename

        pass
