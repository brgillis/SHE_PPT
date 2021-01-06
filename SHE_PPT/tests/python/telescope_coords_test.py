""" @file mdb_test.py

    Created 15 Feb 2018

    Unit tests relating to MDB utility functions
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

__updated__ = "2021-01-06"

from operator import itemgetter
import os

import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT import telescope_coords
from SHE_PPT.constants.test_data import (SYNC_CONF, TEST_FILES_TELESCOPE_COORDS, TEST_DATA_LOCATION,
                                         MDB_PRODUCT_FILENAME, TEST_FOV_TO_FPA_NO_OFFSET_DATA)
import numpy as np


class TestTelescopeCoords:
    """ Class for testing telescope_coords functions
    """

    @classmethod
    def setup_class(cls):

        sync = DataSync(SYNC_CONF, TEST_FILES_TELESCOPE_COORDS)
        sync.download()
        cls.mdb_filename = sync.absolutePath(os.path.join(TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME))
        cls.test_data_filename = sync.absolutePath(os.path.join(TEST_DATA_LOCATION, TEST_FOV_TO_FPA_NO_OFFSET_DATA))

        return

    @classmethod
    def teardown_class(cls):

        return

    def test_load_specs(self):

        # Try changing the specs, and check that loading changes them back properly

        for det_specs in telescope_coords.vis_det_specs, telescope_coords.nisp_det_specs:

            det_specs.gap_dx = -1
            det_specs.gap_dy = -1

            det_specs.detector_pixels_x = -1
            det_specs.detector_pixels_y = -1

            det_specs.detector_activepixels_x = -1
            det_specs.detector_activepixels_y = -1

            det_specs.pixelsize_um = -1

            det_specs.ndet_x = -1
            det_specs.ndet_y = -1

        # Change FOV offset for VIS only, since it isn't in the MDB for NISP
        telescope_coords.vis_det_specs.fov_x_offset_deg = 0.822
        telescope_coords.vis_det_specs.fov_y_offset_deg = 0.

        # Test loading back VIS specs from the MDB
        telescope_coords.load_vis_detector_specs(mdb_files=self.mdb_filename)

        # Check the VIS values are as expected
        assert np.isclose(telescope_coords.vis_det_specs.gap_dx, 1468)
        assert np.isclose(telescope_coords.vis_det_specs.gap_dy, 7528)

        assert telescope_coords.vis_det_specs.detector_pixels_x == 4096
        assert telescope_coords.vis_det_specs.detector_pixels_y == 4136

        assert telescope_coords.vis_det_specs.detector_activepixels_x == 4096
        assert telescope_coords.vis_det_specs.detector_activepixels_y == 4132

        assert np.isclose(telescope_coords.vis_det_specs.pixelsize_um, 12)

        assert telescope_coords.vis_det_specs.ndet_x == 6
        assert telescope_coords.vis_det_specs.ndet_y == 6

        assert np.isclose(telescope_coords.vis_det_specs.fov_x_offset_deg, 0.822)
        assert np.isclose(telescope_coords.vis_det_specs.fov_y_offset_deg, 0.)

        # Test loading back NISP specs from the MDB
        telescope_coords.load_nisp_detector_specs(mdb_files=self.mdb_filename)

        # Check the NISP values are as expected
        assert np.isclose(telescope_coords.nisp_det_specs.gap_dx, 5939.5)
        assert np.isclose(telescope_coords.nisp_det_specs.gap_dy, 11879)

        assert telescope_coords.nisp_det_specs.detector_pixels_x == 2040
        assert telescope_coords.nisp_det_specs.detector_pixels_y == 2040

        assert telescope_coords.nisp_det_specs.detector_activepixels_x == 2040
        assert telescope_coords.nisp_det_specs.detector_activepixels_y == 2040

        assert np.isclose(telescope_coords.nisp_det_specs.pixelsize_um, 18)

        assert telescope_coords.nisp_det_specs.ndet_x == 4
        assert telescope_coords.nisp_det_specs.ndet_y == 4

        assert np.isclose(telescope_coords.nisp_det_specs.fov_x_offset_deg, 0.)
        assert np.isclose(telescope_coords.nisp_det_specs.fov_y_offset_deg, 0.)

        return

    def test_vis_coords(self):

        # Load values from the MDB first
        telescope_coords.load_vis_detector_specs(mdb_files=self.mdb_filename)

        # Mock test - don't have real values to compare to yet

        det_xp = 1409
        det_yp = 879

        det_ix = 4
        det_iy = 2

        ex_foc_x = 17642.0
        ex_foc_y = -100008.0
        ex_fov_x = -0.040837962  # Old: 1.0535
        ex_fov_y = 0.5905  # Old: 0.040837962

        foc_x, foc_y = telescope_coords.get_focal_plane_coords_from_detector(det_xp=det_xp,
                                                                             det_yp=det_yp,
                                                                             det_ix=det_ix,
                                                                             det_iy=det_iy,
                                                                             instrument="VIS")

        assert np.isclose(foc_x, ex_foc_x)
        assert np.isclose(foc_y, ex_foc_y)

        fov_x1, fov_y1 = telescope_coords.get_fov_coords_from_detector(det_xp=det_xp,
                                                                       det_yp=det_yp,
                                                                       det_ix=det_ix,
                                                                       det_iy=det_iy,
                                                                       instrument="VIS")

        assert np.isclose(fov_x1, ex_fov_x)
        assert np.isclose(fov_y1, ex_fov_y)

        fov_x2, fov_y2 = telescope_coords.get_fov_coords_from_focal_plane(foc_x=foc_x,
                                                                          foc_y=foc_y,
                                                                          instrument="VIS")

        assert np.isclose(fov_x2, ex_fov_x)
        assert np.isclose(fov_y2, ex_fov_y)

        return

    def test_nisp_coords(self):

        # Load values from the MDB first
        telescope_coords.load_nisp_detector_specs(mdb_files=self.mdb_filename)

        # Mock test - don't have real values to compare to yet

        det_xp = 1409
        det_yp = 879

        det_ix = 4
        det_iy = 2

        ex_foc_x = 70991.25
        ex_foc_y = -26837.5
        ex_fov_x = 0.1643315972222222
        ex_fov_y = -0.06212384259259259

        foc_x, foc_y = telescope_coords.get_focal_plane_coords_from_detector(det_xp=det_xp,
                                                                             det_yp=det_yp,
                                                                             det_ix=det_ix,
                                                                             det_iy=det_iy,
                                                                             instrument="NISP")

        assert np.isclose(foc_x, ex_foc_x)
        assert np.isclose(foc_y, ex_foc_y)

        fov_x1, fov_y1 = telescope_coords.get_fov_coords_from_detector(det_xp=det_xp,
                                                                       det_yp=det_yp,
                                                                       det_ix=det_ix,
                                                                       det_iy=det_iy,
                                                                       instrument="NISP")

        assert np.isclose(fov_x1, ex_fov_x)
        assert np.isclose(fov_y1, ex_fov_y)

        fov_x2, fov_y2 = telescope_coords.get_fov_coords_from_focal_plane(foc_x=foc_x,
                                                                          foc_y=foc_y,
                                                                          instrument="NISP")

        assert np.isclose(fov_x2, ex_fov_x)
        assert np.isclose(fov_y2, ex_fov_y)

        return

    @pytest.mark.skip("Not a unit test just checking something")
    def test_vis_coords_minmax(self):

        # Load values from the MDB first
        telescope_coords.load_vis_detector_specs(mdb_files=self.mdb_filename)

        # Read in coords from file
        # fov_x,fov_y,fpa_x,fpa_y
        lines = open(self.test_data_filename).readlines()
        fov_to_fpa_data = np.array([[float(pt)
                                     for pt in line.strip().split(',')]
                                    for line in lines if not line.startswith('#')])
        full_data = []
        fov_x_ord = sorted(fov_to_fpa_data, key=itemgetter(0))
        fov_y_ord = sorted(fov_to_fpa_data, key=itemgetter(1))
        print(fov_x_ord[0][0], fov_x_ord[-1][0], fov_y_ord[0][1], fov_y_ord[-1][1])
        assert fov_x_ord[0][0] >= -0.3961
        assert fov_x_ord[-1][0] <= 0.393
        assert (fov_y_ord[0][1] + 0.822) >= 0.4642
        assert (fov_y_ord[-1][1] + 0.822) <= 1.1722

    def test_vis_coords_range(self):

        # Load values from the MDB first
        telescope_coords.load_vis_detector_specs(mdb_files=self.mdb_filename)

        # Read in coords from file
        # fov_x,fov_y,fpa_x,fpa_y
        lines = open(self.test_data_filename).readlines()
        fov_to_fpa_data = np.array([[float(pt)
                                     for pt in line.strip().split(',')]
                                    for line in lines if not line.startswith('#')])
        full_data = []
        for fov_elv_x, fov_elv_y, fpa_elv_x, fpa_elv_y in fov_to_fpa_data:
            # Go from fpa_x,fpa_y --> fov2_x,fov2_y
            if fpa_elv_x > -10000000. and fpa_elv_y > -10000000.:
                # Convert to mm?
                fov2_x, fov2_y = telescope_coords.get_fov_coords_from_focal_plane(
                    fpa_elv_x, fpa_elv_y, 'VIS')
                full_data.append((fov_elv_x, fov_elv_y, fpa_elv_x, fpa_elv_y,
                                  fov2_x, fov2_y, (fov2_x - fov_elv_x), (fov2_y - fov_elv_y)))

        assert np.mean([dt[6] for dt in full_data]) < 0.001
        assert (np.mean([dt[7] for dt in full_data]) - 0.822) < 0.001

    def test_get_vis_quadrant(self):

        # Load values from the MDB
        telescope_coords.load_vis_detector_specs(mdb_files=self.mdb_filename)

        # Test values on the detector, in the left half of detectors
        assert telescope_coords.get_vis_quadrant(x_pix=2047, y_pix=2067, det_iy=1) == "E"
        assert telescope_coords.get_vis_quadrant(x_pix=2048, y_pix=2067, det_iy=2) == "F"
        assert telescope_coords.get_vis_quadrant(x_pix=2047, y_pix=2068, det_iy=3) == "H"
        assert telescope_coords.get_vis_quadrant(x_pix=2048, y_pix=2068, det_iy=1) == "G"

        # Test values on the detector, in the right half of detectors
        assert telescope_coords.get_vis_quadrant(x_pix=2047, y_pix=2067, det_iy=4) == "G"
        assert telescope_coords.get_vis_quadrant(x_pix=2048, y_pix=2067, det_iy=5) == "H"
        assert telescope_coords.get_vis_quadrant(x_pix=2047, y_pix=2068, det_iy=5) == "F"
        assert telescope_coords.get_vis_quadrant(x_pix=2048, y_pix=2068, det_iy=6) == "E"

        # Test that outside values will report "X"
        assert telescope_coords.get_vis_quadrant(x_pix=-1, y_pix=-1, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=1000, y_pix=-1, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=3000, y_pix=-1, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=5000, y_pix=-1, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=5000, y_pix=1000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=5000, y_pix=3000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=5000, y_pix=5000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=3000, y_pix=5000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=1000, y_pix=5000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=-1, y_pix=5000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=-1, y_pix=3000, det_iy=1) == "X"
        assert telescope_coords.get_vis_quadrant(x_pix=-1, y_pix=1000, det_iy=1) == "X"

        return
