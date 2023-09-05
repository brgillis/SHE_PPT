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

from SHE_PPT import product_utility, products
from SHE_PPT.testing.products import MethodsProductTester, ProductTester, SimpleDataProductTester


# We use the common product tester classes to reuse testing code across product types


class TestLe1AocsTimeSeries(SimpleDataProductTester):
    product_class = product_utility.dpdShePlaceholderGeneral
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
    product_class = product_utility.dpdShePlaceholderGeneral
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


class TestSheLensMcCalibration(SimpleDataProductTester):
    product_class = products.she_lensmc_calibration.dpdSheLensMcCalibration
    product_type_name = products.she_lensmc_calibration.product_type_name


class TestSheLensMcChains(SimpleDataProductTester):
    product_class = products.she_lensmc_chains.dpdSheLensMcChains
    product_type_name = products.she_lensmc_chains.product_type_name


class TestSheLensMcTraining(SimpleDataProductTester):
    product_class = products.she_lensmc_training.dpdSheLensMcTraining
    product_type_name = products.she_lensmc_training.product_type_name


class TestSheMeasurements(MethodsProductTester):
    product_class = products.she_measurements.dpdSheMeasurements
    product_type_name = products.she_measurements.product_type_name


class TestSheMomentsMlCalibration(SimpleDataProductTester):
    product_class = products.she_momentsml_calibration.dpdSheMomentsMlCalibration
    product_type_name = products.she_momentsml_calibration.product_type_name


class TestSheMomentsMlTraining(SimpleDataProductTester):
    product_class = products.she_momentsml_training.dpdSheMomentsMlTraining
    product_type_name = products.she_momentsml_training.product_type_name


class TestSheObjectIdList(ProductTester):
    product_class = products.she_object_id_list.dpdSheObjectIdList
    product_type_name = products.she_object_id_list.product_type_name


class TestShePsfLevel1CalibrationParameters(SimpleDataProductTester):
    product_class = products.she_psf_level1_calibration_parameters.dpdShePsfLevel1CalibrationParameters
    product_type_name = products.she_psf_level1_calibration_parameters.product_type_name


class TestShePsfLevel2CalibrationParameters(SimpleDataProductTester):
    product_class = products.she_psf_level2_calibration_parameters.dpdShePsfLevel2CalibrationParameters
    product_type_name = products.she_psf_level2_calibration_parameters.product_type_name


class TestShePsfFieldParameters(SimpleDataProductTester):
    product_class = products.she_psf_field_parameters.dpdShePsfFieldParameters
    product_type_name = products.she_psf_field_parameters.product_type_name


class TestShePsfModelImage(SimpleDataProductTester):
    product_class = products.she_psf_model_image.dpdShePsfModelImage
    product_type_name = products.she_psf_model_image.product_type_name


class TestSheReconciledLensMcChains(SimpleDataProductTester):
    product_class = products.she_reconciled_lensmc_chains.dpdSheReconciledLensMcChains
    product_type_name = products.she_reconciled_lensmc_chains.product_type_name


class TestSheReconciledMeasurements(MethodsProductTester):
    product_class = products.she_reconciled_measurements.dpdSheReconciledMeasurements
    product_type_name = products.she_reconciled_measurements.product_type_name


class TestSheReconciliationConfig(SimpleDataProductTester):
    product_class = products.she_reconciliation_config.dpdSheReconciliationConfig
    product_type_name = products.she_reconciliation_config.product_type_name


class TestSheRegaussCalibration(SimpleDataProductTester):
    product_class = products.she_regauss_calibration.dpdSheRegaussCalibration
    product_type_name = products.she_regauss_calibration.product_type_name


class TestSheRegaussTraining(SimpleDataProductTester):
    product_class = products.she_regauss_training.dpdSheRegaussTraining
    product_type_name = products.she_regauss_training.product_type_name


class TestSheSimulatedCatalog(SimpleDataProductTester):
    product_class = product_utility.dpdSheIntermediateObservationCatalog
    product_type_name = products.she_simulated_catalog.product_type_name


class TestSheSimulationConfig(SimpleDataProductTester):
    product_class = product_utility.dpdSheIntermediateGeneral
    product_type_name = products.she_simulation_config.product_type_name


class TestSheSimulationPlan(SimpleDataProductTester):
    product_class = product_utility.dpdSheIntermediateGeneral
    product_type_name = products.she_simulation_plan.product_type_name


class TestSheStackSegmentationMap(SimpleDataProductTester):
    product_class = products.she_stack_segmentation_map.dpdSheStackReprojectedSegmentationMap
    product_type_name = products.she_stack_segmentation_map.product_type_name


class TestSheStarCatalog(SimpleDataProductTester):
    product_class = products.she_star_catalog.dpdSheStarCatalog
    product_type_name = products.she_star_catalog.product_type_name


class TestSheValidatedMeasurements(MethodsProductTester):
    product_class = products.she_validated_measurements.dpdSheValidatedMeasurements
    product_type_name = products.she_validated_measurements.product_type_name


class TestSheValidationTestResults(ProductTester):
    product_class = products.she_validation_test_results.dpdSheValidationTestResults
    product_type_name = products.she_validation_test_results.product_type_name
