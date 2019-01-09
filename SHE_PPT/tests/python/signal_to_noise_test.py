""" @file signal_to_noise_test.py

    Created 24 October 2018

    Unit tests for the control shear estimation methods.
"""

__updated__ = "2019-01-09"

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

from os.path import join
import pytest

from ElementsServices.DataSync import downloadTestData, localTestFile

from SHE_PPT import magic_values as mv
from SHE_PPT.file_io import read_pickled_product, find_file
from SHE_PPT.signal_to_noise import get_SN_of_image
from SHE_PPT.table_formats.detections import tf as detf
import numpy as np

ex_signal_to_noises = [59, 32, 24, 28.5]

she_frame_location = "WEB/SHE_PPT/test_data_stack.bin"

class TestCase:
    """


    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        self.logdir = join(tmpdir.strpath, "logs")

        return

    def test_get_signal_to_noise(self):
        """Test that the interface for the KSB method works properly.
        """

        # Read in the test data
        she_frame = read_pickled_product(find_file(she_frame_location))

        gain = she_frame.exposures[0].detectors[1, 1].header[mv.gain_label]

        # Get the S/N for each galaxy
        for i, row in enumerate(she_frame.detections_catalogue):
            gal_stack = she_frame.extract_galaxy_stack(row[detf.ID], width=128)

            signal_to_noise_estimates = []
            for exposure in gal_stack.exposures:
                signal_to_noise_estimates.append(get_SN_of_image(exposure.data - exposure.background_map,
                                                                 gain=gain))

            assert np.allclose(signal_to_noise_estimates, ex_signal_to_noises[i],rtol=0.1)

        return
