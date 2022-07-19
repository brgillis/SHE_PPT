""" @file signal_to_noise_test.py

    Created 24 October 2018

    Unit tests for the control shear estimation methods.
"""

__updated__ = "2021-08-12"

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

import numpy as np
import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT import mdb
from SHE_PPT.constants.fits import GAIN_LABEL
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                         SHE_EXPOSURE_SEGMENTATION_MAPS_LISTFILE_FILENAME,
                                         SHE_PSF_MODEL_IMAGES_LISTFILE_FILENAME, SHE_STACK_SEGMENTATION_MAP_FILENAME,
                                         SYNC_CONF, TEST_DATA_LOCATION, TEST_FILES_DATA_STACK, TEST_FILES_MDB,
                                         VIS_CALIBRATED_FRAME_LISTFILE_FILENAME, VIS_STACKED_FRAME_PRODUCT_FILENAME, )
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.signal_to_noise import get_SN_of_image
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.testing.utility import SheTestCase

ex_signal_to_noises = [59, 32]


class TestCase(SheTestCase):
    """


    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):

        # Download the MDB from WebDAV

        self.sync_mdb = DataSync(SYNC_CONF, TEST_FILES_MDB)
        self.sync_mdb.download()
        self.mdb_filename = self.sync_mdb.absolutePath(
            os.path.join(TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME))

        assert os.path.isfile(self.mdb_filename), f"Cannot find file: {self.mdb_filename}"

        mdb.init(self.mdb_filename)

        # Download the data stack files from WebDAV

        self.sync_datastack = DataSync(SYNC_CONF, TEST_FILES_DATA_STACK)
        self.sync_datastack.download()
        self.qualified_data_images_filename = self.sync_datastack.absolutePath(
            os.path.join(TEST_DATA_LOCATION, MER_FINAL_CATALOG_LISTFILE_FILENAME))

        assert os.path.isfile(
            self.qualified_data_images_filename), f"Cannot find file: {self.qualified_data_images_filename}"

        # Get the workdir based on where the data images listfile is
        self.workdir = os.path.split(self.qualified_data_images_filename)[0]
        self.logdir = os.path.join(self.workdir, "logs")

        # Read in the test data
        self.data_stack = SHEFrameStack.read(exposure_listfile_filename=VIS_CALIBRATED_FRAME_LISTFILE_FILENAME,
                                             seg_listfile_filename=SHE_EXPOSURE_SEGMENTATION_MAPS_LISTFILE_FILENAME,
                                             stacked_image_product_filename=VIS_STACKED_FRAME_PRODUCT_FILENAME,
                                             stacked_seg_product_filename=SHE_STACK_SEGMENTATION_MAP_FILENAME,
                                             psf_listfile_filename=SHE_PSF_MODEL_IMAGES_LISTFILE_FILENAME,
                                             detections_listfile_filename=MER_FINAL_CATALOG_LISTFILE_FILENAME,
                                             workdir=self.workdir,
                                             clean_detections=True,
                                             memmap=True,
                                             mode='denywrite',
                                             load_images=False)

    def test_get_signal_to_noise(self):
        """Test that the interface for the KSB method works properly.
        """

        gain = self.data_stack.exposures[0].detectors[1, 1].header[GAIN_LABEL]

        # Get the S/N for each galaxy
        for i, row in enumerate(self.data_stack.detections_catalogue):
            gal_stack = self.data_stack.extract_galaxy_stack(row[mfc_tf.ID], width=128)

            signal_to_noise_estimates = []
            for exposure in gal_stack.exposures:
                signal_to_noise_estimates.append(get_SN_of_image(exposure.data - exposure.background_map,
                                                                 gain=gain))

            assert np.allclose(signal_to_noise_estimates, ex_signal_to_noises[i], rtol=0.1)

        return
