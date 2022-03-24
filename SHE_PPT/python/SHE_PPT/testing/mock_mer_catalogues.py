""" @file mock_data.py

    Created 15 October 2021.

    Utilities to generate mock data for validation tests.
"""

__updated__ = "2021-10-05"

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
import os
from typing import Optional

import numpy as np
from astropy.table import Table

from SHE_PPT.file_io import try_remove_file, write_listfile
from SHE_PPT.logging import getLogger
from SHE_PPT.products.mer_final_catalog import create_dpd_mer_final_catalog
from SHE_PPT.table_formats.mer_final_catalog import (MerFinalCatalogFormat, filter_list, filter_list_ext,
                                                     mer_final_catalog_format, )
from SHE_PPT.testing.constants import MFC_TABLE_FILENAME, MFC_TABLE_LISTFILE_FILENAME, MFC_TABLE_PRODUCT_FILENAME
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockTableGenerator

logger = getLogger(__name__)

# MFC info
MFC_SEED = 57632


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
    """ A class to handle the generation of mock galaxy tables.
    """

    # Attributes with overriding types
    mock_data_generator: MockMFCDataGenerator
    tf: Optional[MerFinalCatalogFormat] = mer_final_catalog_format


def make_mock_mfc_table(seed: int = MFC_SEED, ) -> Table:
    """ Function to generate a mock matched table table.
    """

    mock_data_generator = MockMFCDataGenerator(num_test_points = NUM_TEST_POINTS,
                                               seed = seed)

    mock_table_generator = MockMFCGalaxyTableGenerator(mock_data_generator =
                                                       mock_data_generator)

    return mock_table_generator.get_mock_table()


def write_mock_mfc_table(workdir: str) -> str:
    """ Returns filename of the matched table product.
    """

    write_product_and_table(product = create_dpd_mer_final_catalog(),
                            product_filename = MFC_TABLE_PRODUCT_FILENAME,
                            table = make_mock_mfc_table(seed = MFC_SEED),
                            table_filename = MFC_TABLE_FILENAME)

    # Write the listfile
    write_listfile(os.path.join(workdir, MFC_TABLE_LISTFILE_FILENAME), [MFC_TABLE_PRODUCT_FILENAME])

    return MFC_TABLE_LISTFILE_FILENAME


def cleanup_mock_mfc_table(workdir: str):
    """ To be called in cleanup, deletes matched tables which have been written out.
    """

    try_remove_file(MFC_TABLE_FILENAME, workdir = workdir)
    try_remove_file(MFC_TABLE_PRODUCT_FILENAME, workdir = workdir)
