""" @file mock_tum_cat.py

    Created 24 March 2022

    Utilities to generate mock TU Matched tables for unit tests.
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

from typing import Any, Dict, Optional, Type

import numpy as np

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.file_io import write_xml_product
from SHE_PPT.logging import getLogger
from SHE_PPT.products.she_measurements import create_dpd_she_measurements
from SHE_PPT.table_formats.she_lensmc_tu_matched import lensmc_tu_matched_table_format
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat
from SHE_PPT.testing.mock_data import (MockDataGenerator, NUM_NAN_TEST_POINTS, NUM_TEST_POINTS,
                                       NUM_ZERO_WEIGHT_TEST_POINTS, )
from SHE_PPT.testing.mock_measurements_cat import MockShearEstimateDataGenerator
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator
from SHE_PPT.testing.mock_tu_galaxy_cat import MockTUGalaxyDataGenerator
from SHE_PPT.utility import default_init_if_none, default_value_if_none

logger = getLogger(__name__)

TUM_SEED = 57632
TUM_TABLE_LISTFILE_FILENAME = "mock_tu_matched_catalog_listfile.json"
TUM_TABLE_PRODUCT_FILENAME = "mock_tu_matched_catalog_product.xml"
TUM_TABLE_FILENAME = "data/mock_tu_matched_catalog.fits"
TUM_LENSMC_TABLE_FILENAME = "data/mock_lensmc_tu_matched_catalog.fits"
TUM_KSB_TABLE_FILENAME = "data/mock_ksb_tu_matched_catalog.fits"


class MockTUMatchedDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock TU Matched tables.
    """

    # Overriding base class default values
    tf: SheTUMatchedFormat

    # New attributes for this subclass
    mock_tu_galaxy_data_generator: MockTUGalaxyDataGenerator
    mock_shear_estimate_data_generator: MockShearEstimateDataGenerator
    method: ShearEstimationMethods

    # Attributes used while generating data
    _tu_data: Optional[Dict[str, np.ndarray]] = None
    _se_data: Optional[Dict[str, np.ndarray]] = None

    def __init__(self,
                 method: ShearEstimationMethods,
                 *args,
                 mock_tu_galaxy_data_generator: Optional[MockTUGalaxyDataGenerator] = None,
                 num_nan_test_points: Optional[int] = NUM_NAN_TEST_POINTS,
                 num_zero_weight_test_points: Optional[int] = NUM_ZERO_WEIGHT_TEST_POINTS, **kwargs):
        """ Override init so we can add an input argument for mock tu galaxy data generator.
        """
        super().__init__(*args, **kwargs)

        # Init the method and its table format
        self.method = method
        self.tf = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[method]

        # Init the data generators
        self.mock_tu_galaxy_data_generator = default_init_if_none(mock_tu_galaxy_data_generator,
                                                                  type = MockTUGalaxyDataGenerator,
                                                                  num_test_points = self.num_test_points,
                                                                  seed = self.seed)
        self.mock_shear_estimate_data_generator = MockShearEstimateDataGenerator(method = method,
                                                                                 mock_tu_galaxy_data_generator =
                                                                                 self.mock_tu_galaxy_data_generator,
                                                                                 num_nan_test_points =
                                                                                 num_nan_test_points,
                                                                                 num_zero_weight_test_points =
                                                                                 num_zero_weight_test_points,
                                                                                 num_test_points = self.num_test_points,
                                                                                 seed = self.seed)

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate data by combining the dicts from the two generators.
        """
        self._tu_data = self.mock_tu_galaxy_data_generator.get_data()
        self._se_data = self.mock_shear_estimate_data_generator.get_data()

        self.data = {**self._tu_data, **self._se_data}


class MockTUMatchedTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock mer final catalog tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = MockTUMatchedDataGenerator

    def create_product(self) -> Any:
        return create_dpd_she_measurements()

    # Attributes with overriding types
    tf: Optional[SheTUMatchedFormat] = lensmc_tu_matched_table_format
    seed: int = TUM_SEED
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = TUM_TABLE_FILENAME
    product_filename: str = TUM_TABLE_PRODUCT_FILENAME
    listfile_filename: str = TUM_TABLE_LISTFILE_FILENAME

    # New attributes
    method: ShearEstimationMethods = ShearEstimationMethods.LENSMC

    def __init__(self,
                 *args,
                 mock_data_generator: Optional[MockDataGeneratorType] = None,
                 tf: Optional[SheTUMatchedFormat] = None,
                 seed: Optional[int] = None,
                 num_test_points: Optional[int] = None,
                 method: Optional[ShearEstimationMethods] = None,
                 **kwargs, ):
        """Override initializer so we can pass proper generator.
        """

        # Initialize new attributes for this subtype
        self.method = default_value_if_none(x = method, default_x = self.method)

        # Set up the mock data generator with the proper type
        self.tf = default_value_if_none(x = tf, default_x = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[self.method])

        self.seed = default_value_if_none(x = seed, default_x = self.seed)
        self.num_test_points = default_value_if_none(x = num_test_points, default_x = self.num_test_points)

        mock_data_generator = default_init_if_none(mock_data_generator,
                                                   type = self.mock_data_generator_type,
                                                   tf = self.tf,
                                                   num_test_points = self.num_test_points,
                                                   seed = self.seed,
                                                   method = self.method)

        super().__init__(*args,
                         mock_data_generator = mock_data_generator,
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


def write_mock_tum_tables(workdir: str) -> str:
    """ Convenience function to write tables for both LensMC and KSB in one product
    """

    lensmc_table_generator = MockTUMatchedTableGenerator(method = ShearEstimationMethods.LENSMC,
                                                         seed = TUM_SEED,
                                                         table_filename = TUM_LENSMC_TABLE_FILENAME,
                                                         workdir = workdir)
    lensmc_table_generator.write_mock_table()
    ksb_table_generator = MockTUMatchedTableGenerator(method = ShearEstimationMethods.KSB,
                                                      seed = TUM_SEED + 1,
                                                      table_filename = TUM_KSB_TABLE_FILENAME,
                                                      workdir = workdir)
    ksb_table_generator.write_mock_table()

    # Set up and write the data product
    measurements_table_product = create_dpd_she_measurements()
    measurements_table_product.set_LensMC_filename(TUM_LENSMC_TABLE_FILENAME)
    measurements_table_product.set_KSB_filename(TUM_KSB_TABLE_FILENAME)

    write_xml_product(measurements_table_product, TUM_TABLE_PRODUCT_FILENAME, workdir = workdir)

    return TUM_TABLE_PRODUCT_FILENAME
