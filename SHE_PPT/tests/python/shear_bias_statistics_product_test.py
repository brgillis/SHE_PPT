""" @file shear_bias_statistics_product_test.py

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

__updated__ = "2019-07-15"

import SHE_PPT
from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.math import LinregressStatistics, BFDSumStatistics
from SHE_PPT.products import shear_bias_statistics as prod
import numpy as np


class TestShearBiasStatsProduct(object):
    """A collection of tests for the shear bias statistics data product.

    """

    def test_validation(self, tmpdir):

        workdir = str(tmpdir)

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
                stats[method] = BFDSumStatistics(sums_for_bfd)
        # Create the product
        product = prod.create_dpd_shear_bias_statistics_from_stats(BFD_bias_statistics=stats["BFD"],
                                                                   KSB_bias_statistics=stats["KSB"],
                                                                   LensMC_bias_statistics=stats["LensMC"],
                                                                   MomentsML_bias_statistics=stats["MomentsML"],
                                                                   REGAUSS_bias_statistics=stats["REGAUSS"],
                                                                   workdir=workdir)

        # Check that it validates the schema
        product.validateBinding()

        # Check that it was inited with the proper values
        assert product.get_BFD_bias_statistics(workdir=workdir) == stats["BFD"]
        assert product.get_KSB_bias_statistics(workdir=workdir) == stats["KSB"]
        assert product.get_LensMC_bias_statistics(workdir=workdir) == stats["LensMC"]
        assert product.get_MomentsML_bias_statistics(workdir=workdir) == stats["MomentsML"]
        assert product.get_REGAUSS_bias_statistics(workdir=workdir) == stats["REGAUSS"]

        # Check the general get method works
        stats2 = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            assert product.get_method_statistics(method, workdir=workdir) == stats[method]
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err
            if not method == 'BFD':
                stats2[method] = (LinregressStatistics(x1, y1, y_err),
                                  LinregressStatistics(x2, y2, y_err),)
            else:
                stats2[method] = BFDSumStatistics(sums_for_bfd)

            product.set_method_statistics(method, stats2[method], workdir=workdir)

            assert product.get_method_statistics(method, workdir=workdir) == stats2[method]

        return

    def test_xml_writing_and_reading(self, tmpdir):

        workdir = str(tmpdir)

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
                stats[method] = BFDSumStatistics(sums_for_bfd)
        # Create the product
        product = prod.create_dpd_shear_bias_statistics_from_stats(BFD_bias_statistics=stats["BFD"],
                                                                   KSB_bias_statistics=stats["KSB"],
                                                                   LensMC_bias_statistics=stats["LensMC"],
                                                                   MomentsML_bias_statistics=stats["MomentsML"],
                                                                   REGAUSS_bias_statistics=stats["REGAUSS"],
                                                                   workdir=workdir)

        # Save the product in an XML file
        filename = "she_shear_estimates.xml"
        write_xml_product(product, filename, workdir=workdir)

        # Read back the XML file
        loaded_product = read_xml_product(filename, workdir=workdir)

        # Check that the products coincide
        assert loaded_product.get_BFD_bias_statistics(workdir=workdir).A11 == stats["BFD"].A11
        assert loaded_product.get_KSB_bias_statistics(workdir=workdir)[0].ym == stats["KSB"][0].ym
        assert loaded_product.get_KSB_bias_statistics(workdir=workdir)[1].ym == stats["KSB"][1].ym
        assert loaded_product.get_LensMC_bias_statistics(workdir=workdir)[0].ym == stats["LensMC"][0].ym
        assert loaded_product.get_LensMC_bias_statistics(workdir=workdir)[1].ym == stats["LensMC"][1].ym
        assert loaded_product.get_MomentsML_bias_statistics(workdir=workdir)[0].ym == stats["MomentsML"][0].ym
        assert loaded_product.get_MomentsML_bias_statistics(workdir=workdir)[1].ym == stats["MomentsML"][1].ym
        assert loaded_product.get_REGAUSS_bias_statistics(workdir=workdir)[0].ym == stats["REGAUSS"][0].ym
        assert loaded_product.get_REGAUSS_bias_statistics(workdir=workdir)[1].ym == stats["REGAUSS"][1].ym

        return
