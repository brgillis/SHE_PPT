""" @file mock_mer_final_cat.py

    Created 24 March 2022

    Utilities to generate mock MER Final Catalogs for unit tests.
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
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.table_formats.mer_final_catalog import (MerFinalCatalogFormat, filter_list, filter_list_ext,
                                                     mer_final_catalog_format, )
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator

logger = getLogger(__name__)

# MFC info
MFC_SEED = 57632
MFC_TABLE_LISTFILE_FILENAME = "mock_mer_final_catalog_listfile.json"
MFC_TABLE_PRODUCT_FILENAME = "mock_mer_final_catalog_product.xml"
MFC_TABLE_FILENAME = "data/mock_mer_final_catalog.fits"


class MockMFCDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock MER Final Catalog data.
    """

    # Overring base class default values
    tf: MerFinalCatalogFormat = mer_final_catalog_format
    seed: int = MFC_SEED

    FLUX_MIN: float = 100
    FLUX_MAX: float = 10000

    F_FLUX_ERR_MIN: float = 0.01
    F_FLUX_ERR_MAX: float = 0.50

    BG_MIN: float = 20
    BG_MAX: float = 60

    SIZE_MIN: float = 20
    SIZE_MAX: float = 330

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate galaxy data.
        """

        # Deterministic data
        self.data[self.tf.ID] = self._indices
        self.data[self.tf.seg_ID] = self._indices
        self.data[self.tf.vis_det] = np.ones(self.num_test_points)

        # Randomly-generated data
        self.data[self.tf.gal_x_world] = self._rng.uniform(0., 360., self.num_test_points)
        self.data[self.tf.gal_y_world] = self._rng.uniform(-180., 180., self.num_test_points)

        for f in filter_list_ext + filter_list + ["NIR_STACK"]:
            flux = self._rng.uniform(self.FLUX_MIN, self.FLUX_MAX, self.num_test_points)
            self.data["FLUX_%s_APER" % f] = flux
            self.data["FLUXERR_%s_APER" % f] = flux * self._rng.uniform(self.F_FLUX_ERR_MIN,
                                                                        self.F_FLUX_ERR_MAX,
                                                                        self.num_test_points)

        self.data[self.tf.SEGMENTATION_AREA] = self._rng.uniform(self.SIZE_MIN, self.SIZE_MAX, self.num_test_points)
        self.data[self.tf.bg] = self._rng.uniform(self.BG_MIN, self.BG_MAX, self.num_test_points)


class MockMFCGalaxyTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock mer final catalog tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = MockMFCDataGenerator

    @staticmethod
    def create_product():
        return create_dpd_mer_final_catalog()

    # Attributes with overriding types
    tf: Optional[MerFinalCatalogFormat] = mer_final_catalog_format
    seed: int = MFC_SEED
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = MFC_TABLE_FILENAME
    product_filename: str = MFC_TABLE_PRODUCT_FILENAME
    listfile_filename: str = MFC_TABLE_LISTFILE_FILENAME
