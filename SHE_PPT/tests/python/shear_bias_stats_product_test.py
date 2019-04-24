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

__updated__ = "2019-02-27"

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.math import LinregressStatistics, BFDSumStatistics
from SHE_PPT.products import shear_bias_stats as prod
import numpy as np


class TestShearBiasStatsProduct(object):
    """A collection of tests for the shear bias statistics data product.

    """

    def test_validation(self):

        n = 10
        sums_for_bfd = {'b1': 1.0,
                        'b2': 1.0,
                        'b3': 1.0,
                        'b4': 1.0,
                        'A11': 1.0,
                        'A12': 1.0,
                        'A13': 1.0,
                        'A14': 1.0,
                        'A22': 1.0,
                        'A23': 1.0,
                        'A24': 1.0,
                        'A33': 1.0,
                        'A34': 1.0,
                        'A44': 1.0}

        stats = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err

            if not method == "BFD":
                stats[method] = (LinregressStatistics(x1, y1, y_err),
                                 LinregressStatistics(x2, y2, y_err),)
            else:
                stats[method] = (BFDSumStatistics(sums_for_bfd), None)
        # Create the product
        product = prod.create_dpd_shear_bias_statistics(BFD_bfd_statistics=stats["BFD"][0],
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
        assert product.get_BFD_statistics() == stats["BFD"][0]
        assert product.get_KSB_statistics() == stats["KSB"]
        assert product.get_LensMC_statistics() == stats["LensMC"]
        assert product.get_MomentsML_statistics() == stats["MomentsML"]
        assert product.get_REGAUSS_statistics() == stats["REGAUSS"]

        # Check the general get method works#
        stats2 = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            if not method == 'BFD':
                assert product.get_method_statistics(method) == stats[method]
            else:
                assert product.get_method_statistics(method) == stats[method][0]
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err
            if not method == 'BFD':
                stats2[method] = (LinregressStatistics(x1, y1, y_err),
                                  LinregressStatistics(x2, y2, y_err),)
            else:
                stats2[method] = (BFDSumStatistics(sums_for_bfd), None)

            product.set_method_statistics(method, *stats2[method])

            if not method == 'BFD':
                assert product.get_method_statistics(method) == stats2[method]
            else:
                assert product.get_method_statistics(method) == stats2[method][0]
        pass

    def test_xml_writing_and_reading(self, tmpdir):

        n = 10
        sums_for_bfd = {'b1': 1.0,
                        'b2': 1.0,
                        'b3': 1.0,
                        'b4': 1.0,
                        'A11': 1.0,
                        'A12': 1.0,
                        'A13': 1.0,
                        'A14': 1.0,
                        'A22': 1.0,
                        'A23': 1.0,
                        'A24': 1.0,
                        'A33': 1.0,
                        'A34': 1.0,
                        'A44': 1.0}
        # Create the product
        product = prod.create_dpd_shear_bias_statistics()

        stats = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err
            if not method == 'BFD':
                stats[method] = (LinregressStatistics(x1, y1, y_err),
                                 LinregressStatistics(x2, y2, y_err),)
            else:
                stats[method] = (BFDSumStatistics(sums_for_bfd), None)
        # Create the product
        product = prod.create_dpd_shear_bias_statistics(BFD_bfd_statistics=stats["BFD"][0],
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

        # Save the product in an XML file
        filename = tmpdir.join("she_shear_estimates.xml")
        write_xml_product(product, filename)

        # Read back the XML file
        loaded_product = read_xml_product(filename)

        # Check that the products coincide
        assert loaded_product.get_BFD_statistics().A11 == stats["BFD"][0].A11
        assert loaded_product.get_KSB_statistics()[0].ym == stats["KSB"][0].ym
        assert loaded_product.get_KSB_statistics()[1].ym == stats["KSB"][1].ym
        assert loaded_product.get_LensMC_statistics()[0].ym == stats[
            "LensMC"][0].ym
        assert loaded_product.get_LensMC_statistics()[1].ym == stats[
            "LensMC"][1].ym
        assert loaded_product.get_MomentsML_statistics()[0].ym == stats[
            "MomentsML"][0].ym
        assert loaded_product.get_MomentsML_statistics()[1].ym == stats[
            "MomentsML"][1].ym
        assert loaded_product.get_REGAUSS_statistics()[0].ym == stats[
            "REGAUSS"][0].ym
        assert loaded_product.get_REGAUSS_statistics()[1].ym == stats[
            "REGAUSS"][1].ym

        pass
