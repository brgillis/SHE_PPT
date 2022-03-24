""" @file constants.py

    Created 15 October 2021.

    Constant values used in testing.
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

from SHE_PPT.constants.shear_estimation_methods import (D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS,
                                                        ShearEstimationMethods, )
from SHE_PPT.logging import getLogger

logger = getLogger(__name__)

# Input data filenames
PIPELINE_CONFIG_FILENAME = "pipeline_config.xml"

MEASUREMENTS_TABLE_PRODUCT_FILENAME = "shear_bias_measurements_table.xml"
LENSMC_MEASUREMENTS_TABLE_FILENAME = "data/lensmc_shear_bias_measurements_table.fits"
KSB_MEASUREMENTS_TABLE_FILENAME = "data/ksb_bias_measurements_table.fits"

MATCHED_TABLE_PRODUCT_FILENAME = "shear_bias_matched_table.xml"
LENSMC_MATCHED_TABLE_FILENAME = "data/lensmc_shear_bias_matched_table.fits"
KSB_MATCHED_TABLE_FILENAME = "data/ksb_bias_matched_table.fits"

MFC_TABLE_LISTFILE_FILENAME = "mock_mer_final_catalog_listfile.json"
MFC_TABLE_PRODUCT_FILENAME = "mock_mer_final_catalog_product.xml"
MFC_TABLE_FILENAME = "data/mock_mer_final_catalog.fits"

STAR_CAT_PRODUCT_FILENAME = "mock_she_star_catalog_product.xml"
STAR_CAT_TABLE_FILENAME = "data/mock_she_star_catalog.fits"

# Test data description

# Info about the shear estimation methods and associated tables
TEST_METHOD = ShearEstimationMethods.LENSMC
MATCHED_TF = D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS[TEST_METHOD]
