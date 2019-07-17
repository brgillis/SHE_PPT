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

__updated__ = "2019-07-17"

import os

from astropy.table import Table

import SHE_PPT
from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.math import LinregressStatistics, BFDSumStatistics, BiasMeasurements, linregress_with_errors
from SHE_PPT.products import shear_bias_statistics as prod
from SHE_PPT.table_formats.bias_statistics import calculate_bias_measurements
import numpy as np

seed = 10245

class TestShearBiasStatsProduct(object):
    """A collection of tests for the shear bias statistics data product.

    """

    def test_validation(self, tmpdir):

        workdir = str(tmpdir)
        np.random.seed(seed)

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

        measurements = {}
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
                
            measurements[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                    BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)
            
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

        # Check BFD's statistics are correct
        for val in ("b1", "b2", "b3", "b4", "A11", "A12", "A13", "A14", "A22", "A23", "A24", "A33", "A34", "A44"):

            assert np.isclose(getattr(product.get_BFD_bias_statistics(workdir=workdir), val),
                              getattr(stats["BFD"], val))

        # Check the other methods' statistics are correct
        for val in ("w", "xm", "x2m", "ym", "xym"):
            for new_object, original_object in ((product.get_KSB_bias_statistics(workdir=workdir), stats["KSB"]),
                                                (product.get_LensMC_bias_statistics(
                                                    workdir=workdir), stats["LensMC"]),
                                                (product.get_MomentsML_bias_statistics(
                                                    workdir=workdir), stats["MomentsML"]),
                                                (product.get_REGAUSS_bias_statistics(workdir=workdir), stats["REGAUSS"])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))
                
        # Check that all the bias measurements are correct
        # TODO: Add test of BFD
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for new_object, original_object in ((product.get_KSB_bias_measurements(workdir=workdir), measurements["KSB"]),
                                                (product.get_LensMC_bias_measurements(
                                                    workdir=workdir), measurements["LensMC"]),
                                                (product.get_MomentsML_bias_measurements(
                                                    workdir=workdir), measurements["MomentsML"]),
                                                (product.get_REGAUSS_bias_measurements(workdir=workdir), measurements["REGAUSS"])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))
                

        # Check the general get and set methods work
        stats2 = {}
        measurements2 = {}
        for method in ("BFD", "KSB", "LensMC", "MomentsML", "REGAUSS"):
            x1 = np.linspace(0, n - 1, n, endpoint=True)
            x2 = np.linspace(0, n - 1, n, endpoint=True)
            y_err = 0.25 * np.ones_like(x1)
            y1 = x1 + np.random.randn(n) * y_err
            y2 = x2 + np.random.randn(n) * y_err
            if not method == 'BFD':
                stats2[method] = (LinregressStatistics(x1, y1, y_err),
                                  LinregressStatistics(x2, y2, y_err),)

                product.set_method_bias_statistics(method, stats2[method], workdir=workdir)
            else:
                stats2[method] = BFDSumStatistics(sums_for_bfd)

                product.set_method_bias_statistics(method, stats2[method], workdir=workdir)

                for val in ("b1", "b2", "b3", "b4", "A11", "A12", "A13", "A14", "A22", "A23", "A24", "A33", "A34", "A44"):

                    assert np.isclose(getattr(product.get_BFD_bias_statistics(workdir=workdir), val),
                                      getattr(stats["BFD"], val))
                    
            measurements2[method] = (BiasMeasurements(linregress_with_errors(x1, y1, y_err)),
                                     BiasMeasurements(linregress_with_errors(x2, y2, y_err)),)

        for method in ("KSB", "LensMC", "MomentsML", "REGAUSS"):
            for val in ("w", "xm", "x2m", "ym", "xym"):
                for new_object, original_object in ((product.get_KSB_bias_statistics(workdir=workdir), stats2["KSB"]),
                                                    (product.get_LensMC_bias_statistics(
                                                        workdir=workdir), stats2["LensMC"]),
                                                    (product.get_MomentsML_bias_statistics(
                                                        workdir=workdir), stats2["MomentsML"]),
                                                    (product.get_REGAUSS_bias_statistics(workdir=workdir), stats2["REGAUSS"])):

                    assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                    assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))
                
        # Check that all the updated bias measurements are correct
        # TODO: Add test of BFD
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for new_object, original_object in ((product.get_KSB_bias_measurements(workdir=workdir), measurements2["KSB"]),
                                                (product.get_LensMC_bias_measurements(
                                                    workdir=workdir), measurements2["LensMC"]),
                                                (product.get_MomentsML_bias_measurements(
                                                    workdir=workdir), measurements2["MomentsML"]),
                                                (product.get_REGAUSS_bias_measurements(workdir=workdir), measurements2["REGAUSS"])):

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val))
                
        # Check that all the calculated bias measurements are correct
        # TODO: Add test of BFD
        for val in ("m", "m_err", "c", "c_err", "mc_covar"):
            for filename, method in ((product.get_KSB_bias_statistics_filename(), "KSB"),
                                     (product.get_LensMC_bias_statistics_filename(), "LensMC"),
                                     (product.get_MomentsML_bias_statistics_filename(), "MomentsML"),
                                     (product.get_REGAUSS_bias_statistics_filename(), "REGAUSS")):
                
                table = Table.read(os.path.join(workdir,filename))
                
                new_object = calculate_bias_measurements(table, update=False)
                original_object = measurements2[method]

                assert np.isclose(getattr(new_object[0], val), getattr(original_object[0], val),
                                  rtol=1e-4, atol=1e-5), "Method: " + method
                assert np.isclose(getattr(new_object[1], val), getattr(original_object[1], val),
                                  rtol=1e-4, atol=1e-5), "Method: " + method

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

        for val in ("b1", "b2", "b3", "b4", "A11", "A12", "A13", "A14", "A22", "A23", "A24", "A33", "A34", "A44"):

            assert np.isclose(getattr(loaded_product.get_BFD_bias_statistics(workdir=workdir), val),
                              getattr(stats["BFD"], val))

        for val in ("w", "xm", "x2m", "ym", "xym"):
            for loaded_object, original_object in ((loaded_product.get_KSB_bias_statistics(workdir=workdir), stats["KSB"]),
                                                   (loaded_product.get_LensMC_bias_statistics(
                                                       workdir=workdir), stats["LensMC"]),
                                                   (loaded_product.get_MomentsML_bias_statistics(
                                                       workdir=workdir), stats["MomentsML"]),
                                                   (loaded_product.get_REGAUSS_bias_statistics(workdir=workdir), stats["REGAUSS"])):

                assert np.isclose(getattr(loaded_object[0], val), getattr(original_object[0], val))
                assert np.isclose(getattr(loaded_object[1], val), getattr(original_object[1], val))

        return
