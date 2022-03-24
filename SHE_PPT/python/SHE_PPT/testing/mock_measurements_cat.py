""" @file mock_measurements_cat.py

    Created 24 March 2022

    Utilities to generate mock LensMC Measurements tables for unit tests.
"""

__updated__ = "2022-03-24"

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

from typing import Any, Dict, List, Optional, Type

import numpy as np

from SHE_PPT.constants.classes import BinParameters
from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_measurements import create_dpd_she_measurements
from SHE_PPT.table_formats.she_lensmc_measurements import lensmc_measurements_table_format
from SHE_PPT.table_formats.she_measurements import SheMeasurementsFormat
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat
from SHE_PPT.testing.mock_data import (MockDataGenerator, NUM_NAN_TEST_POINTS, NUM_TEST_POINTS,
                                       NUM_ZERO_WEIGHT_TEST_POINTS, )
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator
from SHE_PPT.testing.mock_tu_galaxy_cat import MockTUGalaxyDataGenerator
from SHE_PPT.utility import default_init_if_none, default_value_if_none

logger = getLogger(__name__)

# Input shear info
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Estimated shear info
EST_SEED = 57632
EST_TABLE_LISTFILE_FILENAME = "mock_shear_estimates_listfile.json"
EST_TABLE_PRODUCT_FILENAME = "mock_shear_estimates_product.xml"
EST_TABLE_FILENAME = "data/mock_shear_estimates.fits"
EST_LENSMC_TABLE_FILENAME = "data/mock_lensmc_shear_estimates.fits"
EST_KSB_TABLE_FILENAME = "data/mock_ksb_shear_estimates.fits"
EST_G_ERR = 0.025
EXTRA_EST_G_ERR = 0.005
EXTRA_EST_G_ERR_ERR = 0.005

D_D_L_D_INPUT_BIAS: Dict[ShearEstimationMethods, Dict[BinParameters, List[Dict[str, float]]]] = {
    ShearEstimationMethods.LENSMC: {BinParameters.TOT: [{"m1"    : 0.05,
                                                         "m1_err": 0.015,
                                                         "c1"    : -0.2,
                                                         "c1_err": 0.05,
                                                         "m2"    : -0.1,
                                                         "m2_err": 0.04,
                                                         "c2"    : 0.01,
                                                         "c2_err": 0.003, }]},
    ShearEstimationMethods.KSB   : {BinParameters.SNR: [{"m1"    : 0.2,
                                                         "m1_err": 0.003,
                                                         "c1"    : -0.3,
                                                         "c1_err": 0.03,
                                                         "m2"    : 0.1,
                                                         "m2_err": 0.21,
                                                         "c2"    : -0.4,
                                                         "c2_err": 0.43, },
                                                        {"m1"    : -0.3,
                                                         "m1_err": 0.031,
                                                         "c1"    : -0.5,
                                                         "c1_err": 0.05,
                                                         "m2"    : 0.35,
                                                         "m2_err": 0.15,
                                                         "c2"    : 0.,
                                                         "c2_err": 0.1,
                                                         }]}}


class MockShearEstimateDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock shear estimates data.
    """

    # Overring base class default values
    tf: SheMeasurementsFormat
    seed: int = 75275

    # New attributes for this subclass
    mock_tu_galaxy_data_generator: MockTUGalaxyDataGenerator
    method: ShearEstimationMethods
    num_nan_test_points: int = NUM_NAN_TEST_POINTS
    num_zero_weight_test_points: int = NUM_ZERO_WEIGHT_TEST_POINTS
    num_good_test_points: int

    # Attributes used while generating data
    _tu_data: Optional[Dict[str, np.ndarray]] = None
    _tu_tf: Optional[SheTUMatchedFormat] = None

    def __init__(self,
                 method: ShearEstimationMethods,
                 mock_tu_galaxy_data_generator: Optional[MockTUGalaxyDataGenerator] = None,
                 num_nan_test_points: Optional[int] = NUM_NAN_TEST_POINTS,
                 num_zero_weight_test_points: Optional[int] = NUM_ZERO_WEIGHT_TEST_POINTS,
                 *args, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[method]

        # Init the data generator
        self.mock_tu_galaxy_data_generator = default_init_if_none(mock_tu_galaxy_data_generator,
                                                                  type = MockTUGalaxyDataGenerator)

        # Init and check the numbers of test points
        self.num_test_points = self.mock_tu_galaxy_data_generator.num_test_points
        self.num_nan_test_points = default_value_if_none(num_nan_test_points, self.num_nan_test_points)
        self.num_zero_weight_test_points = default_value_if_none(num_zero_weight_test_points, self.num_nan_test_points)
        self.num_good_test_points = self.num_test_points - self.num_nan_test_points - self.num_zero_weight_test_points
        assert self.num_test_points >= self.num_good_test_points > 0

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        self.data[self.tf.ID] = self._indices

        # Get the TU data generator and table format
        self._tu_data = self.mock_tu_galaxy_data_generator.get_data()
        self._tu_tf = self.mock_tu_galaxy_data_generator.tf

        self.data[self.tf.ID] = self._indices

        # Generate random noise for output data
        l_extra_g_err = EXTRA_EST_G_ERR + EXTRA_EST_G_ERR_ERR * self._rng.standard_normal(self.num_test_points)
        l_g_err = np.sqrt(EST_G_ERR ** 2 + l_extra_g_err ** 2)
        l_g1_deviates = l_g_err * self._rng.standard_normal(self.num_test_points)
        l_g2_deviates = l_g_err * self._rng.standard_normal(self.num_test_points)

        # Save the error in the table
        self.data[self.tf.g1_err] = l_g_err
        self.data[self.tf.g2_err] = l_g_err
        self.data[self.tf.weight] = 0.5 * l_g_err ** -2

        # Fill in rows with mock output data - this bit depends on which method we're using
        d_l_d_method_input_bias = D_D_L_D_INPUT_BIAS[self.method]
        if self.method == ShearEstimationMethods.LENSMC:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.TOT][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.TOT][0]
        else:
            d_bias_0m2 = d_l_d_method_input_bias[BinParameters.SNR][0]
            d_bias_1m2 = d_l_d_method_input_bias[BinParameters.SNR][1]

        g1_0m2 = d_bias_0m2["c1"] + (1 + d_bias_0m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates
        g1_1m2 = d_bias_1m2["c1"] + (1 + d_bias_1m2["m1"]) * -self._tu_data[self._tu_tf.tu_gamma1] + l_g1_deviates

        g2_0m2 = d_bias_0m2["c2"] + (1 + d_bias_0m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates
        g2_1m2 = d_bias_1m2["c2"] + (1 + d_bias_1m2["m2"]) * self._tu_data[self._tu_tf.tu_gamma2] + l_g2_deviates

        # Add to table, flipping g1 due to SIM's format
        self.data[self.tf.g1] = np.where(self._indices % 2 < 1, g1_0m2, g1_1m2)
        self.data[self.tf.g2] = np.where(self._indices % 2 < 1, g2_0m2, g2_1m2)

        # Flag the last bit of data as bad or zero weight
        self.data[self.tf.g1][-self.num_nan_test_points - self.num_zero_weight_test_points:
                              -self.num_zero_weight_test_points] = np.NaN
        self.data[self.tf.g1_err][-self.num_nan_test_points - self.num_zero_weight_test_points:] = np.NaN
        self.data[self.tf.g2][-self.num_nan_test_points - self.num_zero_weight_test_points:
                              -self.num_zero_weight_test_points] = np.NaN
        self.data[self.tf.g2_err][-self.num_nan_test_points - self.num_zero_weight_test_points:] = np.NaN

        self.data[self.tf.g1_err][-self.num_zero_weight_test_points:] = np.inf
        self.data[self.tf.g2_err][-self.num_zero_weight_test_points:] = np.inf
        self.data[self.tf.weight][-self.num_zero_weight_test_points:] = 0

        # Set the fit flags
        self.data[self.tf.fit_flags] = np.where(self._indices < self.num_good_test_points, 0,
                                                np.where(self._indices < self.num_good_test_points +
                                                         self.num_nan_test_points,
                                                         1,
                                                         0))


class MockShearEstimateTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock mer final catalog tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = MockShearEstimateDataGenerator

    @staticmethod
    def create_product() -> Any:
        return create_dpd_she_measurements()

    # Attributes with overriding types
    tf: Optional[SheMeasurementsFormat] = lensmc_measurements_table_format
    seed: int = EST_SEED
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = EST_TABLE_FILENAME
    product_filename: str = EST_TABLE_PRODUCT_FILENAME
    listfile_filename: str = EST_TABLE_LISTFILE_FILENAME

    # New attributes
    method: ShearEstimationMethods = ShearEstimationMethods.LENSMC

    def __init__(self,
                 *args,
                 mock_data_generator: Optional[MockDataGeneratorType] = None,
                 tf: Optional[SheMeasurementsFormat] = None,
                 seed: Optional[int] = None,
                 num_test_points: Optional[int] = None,
                 method: Optional[ShearEstimationMethods] = None,
                 **kwargs, ):
        # Initialize new attributes for this subtype
        self.method = default_value_if_none(x = method, default_x = self.method)

        # Set up the mock data generator with the proper type
        tf = default_value_if_none(x = tf, default_x = D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS[self.method])

        seed = default_value_if_none(x = seed, default_x = self.seed)
        num_test_points = default_value_if_none(x = num_test_points, default_x = self.num_test_points)

        mock_data_generator = default_init_if_none(mock_data_generator,
                                                   type = self.mock_data_generator_type,
                                                   tf = tf,
                                                   num_test_points = num_test_points,
                                                   seed = seed,
                                                   method = self.method)

        super().__init__(*args,
                         mock_data_generator = mock_data_generator,
                         tf = tf,
                         seed = seed,
                         num_test_points = num_test_points,
                         **kwargs)

    def write_mock_product(self) -> str:
        """ Override write_mock_product here, since we need to use the proper method to set the filename
        """

        self.write_mock_table()

        # Set up and write the data product
        measurements_table_product = self.create_product()
        measurements_table_product.set_method_filename(self.method, self.table_filename)

        write_xml_product(measurements_table_product, self.product_filename, workdir = self.workdir)

        return self.product_filename


def write_mock_measurements_tables(workdir: str) -> str:
    """ Convenience function to write tables for both LensMC and KSB in one product
    """

    lensmc_table_generator = MockShearEstimateTableGenerator(method = ShearEstimationMethods.LENSMC,
                                                             seed = EST_SEED,
                                                             table_filename = EST_LENSMC_TABLE_FILENAME,
                                                             workdir = workdir)
    lensmc_table_generator.write_mock_table()
    ksb_table_generator = MockShearEstimateTableGenerator(method = ShearEstimationMethods.KSB,
                                                          seed = EST_SEED + 1,
                                                          table_filename = EST_KSB_TABLE_FILENAME,
                                                          workdir = workdir)
    ksb_table_generator.write_mock_table()

    # Set up and write the data product
    measurements_table_product = create_dpd_she_measurements()
    measurements_table_product.set_LensMC_filename(EST_LENSMC_TABLE_FILENAME)
    measurements_table_product.set_KSB_filename(EST_KSB_TABLE_FILENAME)

    write_xml_product(measurements_table_product, EST_TABLE_PRODUCT_FILENAME, workdir = workdir)

    return EST_TABLE_PRODUCT_FILENAME
