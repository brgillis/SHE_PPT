""" @file signal_to_noise_test.py

    Created 24 October 2018

    Unit tests for the control shear estimation methods.
"""

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

__updated__ = "2020-06-10"

import os
from os.path import join
import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT import magic_values as mv
from SHE_PPT import mdb
from SHE_PPT.file_io import read_pickled_product, find_file
from SHE_PPT.logging import getLogger
from SHE_PPT.she_frame_stack import SHEFrameStack
from SHE_PPT.signal_to_noise import get_SN_of_image
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_formats.shear_estimates import tf as setf
import numpy as np

ex_signal_to_noises = [59, 32]

test_data_location = "/tmp"

data_images_filename = "data/data_images.json"
segmentation_images_filename = "data/segmentation_images.json"
stacked_image_filename = "data/stacked_image.xml"
stacked_segmentation_image_filename = "data/stacked_segm_image.xml"
psf_images_and_tables_filename = "data/psf_images_and_tables.json"
detections_tables_filename = "data/detections_tables.json"


class TestCase:
    """


    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):

        # Download the MDB from WebDAV

        self.sync_mdb = DataSync("testdata/sync.conf", "testdata/test_mdb.txt")
        self.sync_mdb.download()
        self.mdb_filename = self.sync_mdb.absolutePath("SHE_PPT_v8/sample_mdb.xml")

        assert os.path.isfile(self.mdb_filename), f"Cannot find file: SHE_PPT/sample_mdb.xml"

        mdb.init(self.mdb_filename)

        # Download the data stack files from WebDAV

        self.sync_datastack = DataSync("testdata/sync.conf", "testdata/test_data_stack.txt")
        self.sync_datastack.download()
        self.qualified_data_images_filename = self.sync_datastack.absolutePath("SHE_CTE_v8/data/data_images.json")

        assert os.path.isfile(self.qualified_data_images_filename), f"Cannot find file: {self.qualified_data_images_filename}"

        # Get the workdir based on where the data images listfile is
        self.workdir, datadir = os.path.split(os.path.split(self.qualified_data_images_filename)[0])
        assert datadir == "data", f"Data directory is not as expected in {self.qualified_data_images_filename}"
        self.logdir = os.path.join(self.workdir, "logs")
        
        # Read in the test data
        self.data_stack = SHEFrameStack.read(exposure_listfile_filename=data_images_filename,
                                             seg_listfile_filename=segmentation_images_filename,
                                             stacked_image_product_filename=stacked_image_filename,
                                             stacked_seg_product_filename=stacked_segmentation_image_filename,
                                             psf_listfile_filename=psf_images_and_tables_filename,
                                             detections_listfile_filename=detections_tables_filename,
                                             workdir=self.workdir,
                                             clean_detections=True,
                                             memmap=True,
                                             mode='denywrite')

    def test_get_signal_to_noise(self):
        """Test that the interface for the KSB method works properly.
        """

        gain = self.data_stack.exposures[0].detectors[1, 1].header[mv.gain_label]

        # Get the S/N for each galaxy
        for i, row in enumerate(self.data_stack.detections_catalogue):
            gal_stack = self.data_stack.extract_galaxy_stack(row[detf.ID], width=128)

            signal_to_noise_estimates = []
            for exposure in gal_stack.exposures:
                signal_to_noise_estimates.append(get_SN_of_image(exposure.data - exposure.background_map,
                                                                 gain=gain))

            assert np.allclose(signal_to_noise_estimates, ex_signal_to_noises[i], rtol=0.1)

        return
