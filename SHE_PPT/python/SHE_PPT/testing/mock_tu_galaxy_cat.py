""" @file mock_data.py

    Created 24 March 2022

    Utilities to generate mock TU Galaxy tables for unit tests.
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
from typing import Optional, Type

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.she_lensmc_tu_matched import SheLensMcTUMatchedFormat, lensmc_tu_matched_table_format
from SHE_PPT.table_formats.she_tu_matched import SheTUMatchedFormat, she_tu_matched_table_format
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator
from ST_DataModelBindings.dpd.sim.raw.galaxycatalogproduct_stub import dpdGalaxyCatalogProduct

logger = getLogger(__name__)

# Input shear info
INPUT_G_MIN = -0.7
INPUT_G_MAX = 0.7

# Table info
TUG_SEED = 3513
TUG_TABLE_LISTFILE_FILENAME = "mock_tu_gal_listfile.json"
TUG_TABLE_PRODUCT_FILENAME = "mock_tu_gal_product.xml"
TUG_TABLE_FILENAME = "data/mock_tu_gal.fits"


class MockTUGalaxyDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock galaxy catalog data.
    """

    # Overring base class default values
    tf: SheTUMatchedFormat = she_tu_matched_table_format
    seed: int = TUG_SEED

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        self.data[self.tf.ID] = self._indices

        # Fill in input data
        self.data[self.tf.tu_gamma1] = -np.linspace(INPUT_G_MIN, INPUT_G_MAX, self.num_test_points)
        self.data[self.tf.tu_gamma2] = np.linspace(INPUT_G_MAX, INPUT_G_MIN, self.num_test_points)
        self.data[self.tf.tu_kappa] = np.zeros_like(self.data[self.tf.tu_gamma1])


class MockTUGalaxyTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock true universe galaxy tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = MockTUGalaxyDataGenerator
    product_type: Optional[Type] = dpdGalaxyCatalogProduct

    # Attributes with overriding types
    tf: Optional[SheLensMcTUMatchedFormat] = lensmc_tu_matched_table_format
    seed: int = TUG_SEED
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = TUG_TABLE_FILENAME
    product_filename: str = TUG_TABLE_PRODUCT_FILENAME
    listfile_filename: str = TUG_TABLE_LISTFILE_FILENAME
