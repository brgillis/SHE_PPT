""" @file products_test.py

    Created 16 August 2021

    Unit tests data products
"""

__updated__ = "2021-08-16"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from SHE_PPT import products
from SHE_PPT.testing.products import ProductTester, SimpleDataProductTester, MethodsProductTester

# We use the common product tester classes to reuse testing code across product types


class TestLe1AocsTimeSeries(SimpleDataProductTester):
    product_class = products.le1_aocs_time_series.dpdShePlaceholderGeneral
    product_type_name = products.le1_aocs_time_series.product_type_name


class TestMerFinalCatalog(SimpleDataProductTester):
    product_class = products.mer_final_catalog.dpdMerFinalCatalog
    product_type_name = products.mer_final_catalog.product_type_name


class TestMerSegmentationMap(SimpleDataProductTester):
    product_class = products.mer_segmentation_map.dpdMerSegmentationMap
    product_type_name = products.mer_segmentation_map.product_type_name


class TestSheAnalysisConfig(SimpleDataProductTester):
    product_class = products.she_analysis_config.dpdSheAnalysisConfig
    product_type_name = products.she_analysis_config.product_type_name


class TestSheBiasStatistics(SimpleDataProductTester):
    product_class = products.she_bias_statistics.dpdSheIntermediateGeneral
    product_type_name = products.she_bias_statistics.product_type_name


class TestSheCommonCalibration(MethodsProductTester):
    product_class = products.she_common_calibration.dpdSheCommonCalibration
    product_type_name = products.she_common_calibration.product_type_name


class TestSheExpectedShearValidationStatistics(SimpleDataProductTester):
    product_class = products.she_expected_shear_validation_statistics.dpdShePlaceholderGeneral
    product_type_name = products.she_expected_shear_validation_statistics.product_type_name


class TestSheExposureSegmentationMap(SimpleDataProductTester):
    product_class = products.she_exposure_segmentation_map.dpdSheExposureReprojectedSegmentationMap
    product_type_name = products.she_exposure_segmentation_map.product_type_name


class TestSheGalaxyPopulationPriors(SimpleDataProductTester):
    product_class = products.she_galaxy_population_priors.dpdSheGalaxyPopulationPriors
    product_type_name = products.she_galaxy_population_priors.product_type_name


class TestSheKsbCalibration(SimpleDataProductTester):
    product_class = products.she_ksb_calibration.dpdSheKsbCalibration
    product_type_name = products.she_ksb_calibration.product_type_name


class TestSheKsbTraining(SimpleDataProductTester):
    product_class = products.she_ksb_training.dpdSheKsbTraining
    product_type_name = products.she_ksb_training.product_type_name
