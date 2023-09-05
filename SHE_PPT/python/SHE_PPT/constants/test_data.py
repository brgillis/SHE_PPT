""" @file test_data.py

    Created 6 Jan 2021

    Constants related to test data
"""

__updated__ = "2021-08-25"

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

from os.path import join

SYNC_LOCATION = "testdata"
SYNC_CONF = join(SYNC_LOCATION, "sync.conf")

TEST_FILES_MDB = join(SYNC_LOCATION, "test_mdb.txt")
TEST_FILES_DATA_STACK = join(SYNC_LOCATION, "test_data_stack.txt")

TEST_DATA_LOCATION = "SHE_PPT_9_5"
TEST_DATADIR = "/tmp"

# Files from the MDB list
MDB_PRODUCT_FILENAME = "sample_mdb-SC8.xml"

# Files from the data_stack list
VIS_CALIBRATED_FRAME_LISTFILE_FILENAME = "vis_calibrated_frames.json"
VIS_STACKED_FRAME_PRODUCT_FILENAME = "vis_stacked_image.xml"
MER_FINAL_CATALOG_PRODUCT_FILENAME = "EUC_SHE_P-MER-FINAL-CAT_BUKRTILMXZI3ADHVZ_20200721T162818.092086Z_08.02.xml"
MER_FINAL_CATALOG_TABLE_FILENAME = "EUC_SHE_MER-FINAL-CAT_BUKRTILMXZI3ADHVZ_20200721T162818.092086Z_08.02.fits"
MER_FINAL_CATALOG_LISTFILE_FILENAME = "mer_final_catalogs.json"
LENSMC_MEASUREMENTS_TABLE_FILENAME = "mock_lensmc_measurements.fits"
SHE_EXPOSURE_SEGMENTATION_MAPS_LISTFILE_FILENAME = "she_exposure_reprojected_segmentation_maps.json"
SHE_STACK_SEGMENTATION_MAP_FILENAME = "she_stack_reprojected_segmentation_map.xml"
SHE_PSF_MODEL_IMAGES_LISTFILE_FILENAME = "she_psf_model_images.json"
SHE_VALIDATED_MEASUREMENTS_PRODUCT_FILENAME = "she_validated_measurements.xml"
SHE_EXTENDED_CATALOG_PRODUCT_FILENAME = "she_ext_cat.xml"
SHE_EXTENDED_CATALOG_TABLE_FILENAME = "she_ext_cat.fits"

# Files from the telescope_coords list
TEST_FOV_TO_FPA_NO_OFFSET_DATA = "testFovToFPA_noOffset.dat"
