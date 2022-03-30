""" @file mock_she_star_cat.py

    Created 24 March 2022

    Utilities to generate mock SHE star catalogs for unit tests.
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
from typing import Any, Optional, Type

import numpy as np
from scipy.stats import chi2

from SHE_PPT.detector import VIS_DETECTOR_PIXELS_X, VIS_DETECTOR_PIXELS_Y
from SHE_PPT.products.she_star_catalog import create_dpd_she_star_catalog
from SHE_PPT.table_formats.she_star_catalog import SHE_STAR_CAT_TF, SheStarCatalogFormat
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.testing.mock_tables import MockDataGeneratorType, MockTableGenerator

# Constants describing how to generate mock star data
STAR_CAT_SEED = 152314
STAR_CAT_TABLE_LISTFILE_FILENAME = "mock_she_star_catalog_listfile.json"
STAR_CAT_TABLE_PRODUCT_FILENAME = "mock_she_star_catalog_product.xml"
STAR_CAT_TABLE_FILENAME = "data/mock_she_star_catalog.fits"
STAR_CAT_POS_ERR_PIX = 0.2
STAR_CAT_PIXEL_SCALE = 0.1 / 3600
STAR_CAT_FLUX_MIN = 10
STAR_CAT_FLUX_MAX = 100
STAR_CAT_FLUX_ERR = 5
STAR_CAT_SIGMA_E = 0.2
STAR_CAT_E_ERR = 0.01
STAR_CAT_NUM_UNMASKED_PER_STAR = 100
STAR_CAT_NUM_FITTED_PER_GROUP = 10


class MockStarCatDataGenerator(MockDataGenerator):
    """ A class to handle the generation of mock star catalog data.
    """

    # Overring base class default values
    tf: SheStarCatalogFormat = SHE_STAR_CAT_TF
    seed: int = STAR_CAT_SEED

    # Implement abstract methods
    def _generate_unique_data(self):
        """ Generate mock star data.
        """

        self.data[self.tf.id] = self._indices

        # Fill in catalog data

        # Detector position - random detector for each mock star
        self.data[self.tf.det_x] = self._rng.integers(low = 1, high = 6, size = self.num_test_points)
        self.data[self.tf.det_y] = self._rng.integers(low = 1, high = 6, size = self.num_test_points)

        # Position on detector - random uniform position
        self.data[self.tf.x] = self._rng.uniform(low = 0, high = VIS_DETECTOR_PIXELS_X, size = self.num_test_points)
        self.data[self.tf.y] = self._rng.uniform(low = 0, high = VIS_DETECTOR_PIXELS_Y, size = self.num_test_points)

        # Position on error - same for all
        self.data[self.tf.x_err] = STAR_CAT_POS_ERR_PIX * self._ones
        self.data[self.tf.y_err] = STAR_CAT_POS_ERR_PIX * self._ones

        # Sky position - use pixel-scale only WCS here for simplicity
        self.data[self.tf.ra] = -self.data[self.tf.x] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.dec] = self.data[self.tf.y] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.ra_err] = self.data[self.tf.x_err] * STAR_CAT_PIXEL_SCALE
        self.data[self.tf.dec_err] = self.data[self.tf.y_err] * STAR_CAT_PIXEL_SCALE

        # Uniform distribution for flux, fixed value for flux error
        self.data[self.tf.flux] = self._rng.uniform(low = STAR_CAT_FLUX_MIN, high = STAR_CAT_FLUX_MAX,
                                                    size = self.num_test_points)
        self.data[self.tf.flux_err] = STAR_CAT_FLUX_ERR * self._ones

        # Gaussian distributions for e1 and e2, fixed values for errors
        self.data[self.tf.e1] = self._rng.normal(loc = 0, scale = STAR_CAT_SIGMA_E, size = self.num_test_points)
        self.data[self.tf.e2] = self._rng.normal(loc = 0, scale = STAR_CAT_SIGMA_E, size = self.num_test_points)
        self.data[self.tf.e1_err] = STAR_CAT_E_ERR * self._ones
        self.data[self.tf.e2_err] = STAR_CAT_E_ERR * self._ones

        # All even-indexed used for fit
        self.data[self.tf.used_for_fit] = np.where(self._indices % 2 == 0, self._ones.astype(bool),
                                                   self._zeros.astype(bool))

        # Assign those where modulo 4 = 0 to group 0, others to group 1
        self.data[self.tf.group_id] = np.where(self._indices % 4 == 0, 0, 1)

        # Get a list of group IDs and the number of groups
        l_group_ids = np.unique(self.data[self.tf.group_id])

        # Determine data for each group
        d_group_num_unmasked_pix = {}
        d_group_num_fitted_params = {}
        d_group_chisqs = {}
        for group_id in l_group_ids:
            num_stars_in_group = (self.data[self.tf.group_id] == group_id).sum()
            d_group_num_unmasked_pix[group_id] = num_stars_in_group * STAR_CAT_NUM_UNMASKED_PER_STAR
            d_group_num_fitted_params[group_id] = STAR_CAT_NUM_FITTED_PER_GROUP

            dofs = d_group_num_unmasked_pix[group_id] - d_group_num_fitted_params[group_id]

            p = self._rng.uniform()
            d_group_chisqs[group_id] = chi2.ppf(p, df = dofs)

        # And assign this data to arrays for the table, applying the dicts to each element of the arrays
        self.data[self.tf.group_unmasked_pix] = np.array([d_group_num_unmasked_pix[self.data[self.tf.group_id][i]]
                                                          for i in self._indices])
        self.data[self.tf.group_num_fitted_params] = np.array([d_group_num_fitted_params[self.data[self.tf.group_id][i]]
                                                               for i in self._indices])
        self.data[self.tf.group_chisq] = np.array([d_group_chisqs[self.data[self.tf.group_id][i]]
                                                   for i in self._indices])

        # Assign per-star data
        self.data[self.tf.star_unmasked_pix] = STAR_CAT_NUM_UNMASKED_PER_STAR * self._ones

        l_p = self._rng.uniform(size = self.num_test_points)
        self.data[self.tf.star_chisq] = chi2.ppf(l_p, df = STAR_CAT_NUM_UNMASKED_PER_STAR)


class MockSheStarCatTableGenerator(MockTableGenerator):
    """ A class to handle the generation of mock mer final catalog tables.
    """

    mock_data_generator_type: Type[MockDataGeneratorType] = MockStarCatDataGenerator

    def create_product(self) -> Any:
        return create_dpd_she_star_catalog()

    # Attributes with overriding types
    tf: Optional[SheStarCatalogFormat] = SHE_STAR_CAT_TF
    seed: int = STAR_CAT_SEED
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = STAR_CAT_TABLE_FILENAME
    product_filename: str = STAR_CAT_TABLE_PRODUCT_FILENAME
    listfile_filename: str = STAR_CAT_TABLE_LISTFILE_FILENAME
