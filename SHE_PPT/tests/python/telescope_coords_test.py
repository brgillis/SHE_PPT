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

__updated__ = "2020-01-20"

import os

import pytest

from ElementsServices.DataSync import DataSync
from SHE_PPT import telescope_coords
import numpy as np


class TestTelescopeCoords:
    """ Class for testing telescope_coords functions
    """

    @classmethod
    def setup_class(cls):

        cls.sync = DataSync("testdata/sync.conf", "testdata/test_mdb.txt")
        cls.sync.download()
        cls.mdb_filename = cls.sync.absolutePath("SHE_PPT/sample_mdb.xml")

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
        ex_fov_x = 0.8628379629629629
        ex_fov_y = -0.23149999999999998

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
