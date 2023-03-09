#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
:file: tests/python/get_fov_coords_test.py

:date: 09/03/22
:author: Gordon Gibb
"""

import pytest

import numpy as np
from astropy.wcs import WCS

from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_frame import SHEFrame, CoordTuple

PIXEL_SHAPE = (4096, 4136)
PIXEL_SIZE = 0.1 / 3600.0


@pytest.fixture
def frame():
    """Returns a valid SHEFrame with 36 detectors with valid WCSs but no data."""

    def create_wcs(ra, dec, shape=PIXEL_SHAPE, pixel_size=PIXEL_SIZE):
        w = WCS(naxis=2)
        w.wcs.crpix = [1, 1]
        w.wcs.crval = [ra, dec]
        w.wcs.cdelt = [pixel_size, pixel_size]
        w.wcs.ctype = ["RA---TAN", "DEC--TAN"]
        w.pixel_shape = shape

        return w

    # a quirk of SHEFrame is that it has an array of 7x7 detectors, with the 0th row/column as Nones
    detector_array = []
    for j in range(7):
        row = []
        for i in range(7):
            if j == 0 or i == 0:
                row.append(None)
            else:
                ra = (i - 1) * (PIXEL_SIZE * 5000)
                dec = (j - 1) * (PIXEL_SIZE * 5000)
                w = create_wcs(ra, dec)
                img = SHEImage(data=None, wcs=w)
                img.shape = PIXEL_SHAPE
                row.append(img)
        detector_array.append(row)

    detector_array = np.asarray(detector_array)

    frame = SHEFrame(detector_array)

    return frame


class TestGetFovCoords:
    def test_api(self, frame):
        """
        Tests that SHEFrame.get_fov_coords behaves correctly given inputs
        """

        # pick a point definitely outside the FOV of the detectors, ensure None is profuced
        bad_ra, bad_dec = frame.detectors[1, 1].pix2world(-500, -500)

        assert frame.get_fov_coords(bad_ra, bad_dec) is None, "Valid FOV coords were returned for an invalid position"

        # Now try the return_det_coords_too argument, should also return None
        assert (
            frame.get_fov_coords(bad_ra, bad_dec, return_det_coords_too=True) is None
        ), "Valid FOV coords were returned for an invalid position"

        # pick a valid point (centre of a detector)
        x = PIXEL_SHAPE[0] / 2
        y = PIXEL_SHAPE[1] / 2
        det_x = 4
        det_y = 5
        ra, dec = frame.detectors[det_y, det_x].pix2world(x, y)

        # Make sure it returns numbers (we cannot verify the correctness of the numbers)
        x_fov, y_fov = frame.get_fov_coords(ra, dec)
        assert type(x_fov) is float
        assert type(y_fov) is float

        # Call with return_det_coords_too=True, should return a CoordTuple
        coordtuple = frame.get_fov_coords(ra, dec, return_det_coords_too=True)
        assert type(coordtuple) is CoordTuple, "Expected CoordTuple, but got %s" % type(coordtuple)
        assert coordtuple.detno_x == det_x, "get_fov_coords returned the wrong x detector"
        assert coordtuple.detno_y == det_y, "get_fov_coords returned the wrong y detector"
        assert np.isclose(coordtuple.x_det, x), "get_fov_coords did not return the correct detector x pixel"
        assert np.isclose(coordtuple.y_det, y), "get_fov_coords did not return the correct detector y pixel"
        # ensure the x/y_fovs are the same as if this is called without return_det_coords_too
        assert coordtuple.x_fov == x_fov, "get_fov_coords did not return the expected x_fov"
        assert coordtuple.y_fov == y_fov, "get_fov_coords did not return the expected x_fov"

    def test_no_transpose(self, frame):
        # This test checks to see if SHEFrame.get_fov_coords incorrectly transposes the detectors
        #
        # Vertical distance between 1-1 and 2-1 should be greater
        # than horizontal distance between 1-1 and 1-2
        #
        #       2-1     |  |    2-2
        #   ____________|  |__________
        #        ^
        #        |
        #   ____________    __________
        #               |  |
        #       1-1     |->|    1-2

        # sky coords of upper right corner of 1-1
        ra11, dec11 = frame.detectors[1, 1].pix2world(PIXEL_SHAPE[0], PIXEL_SHAPE[1])
        # sky coords of upper left corner of 1-2
        ra12, dec12 = frame.detectors[1, 2].pix2world(1, PIXEL_SHAPE[1])
        # sky coords of lower right corner of 2-1
        ra21, dec21 = frame.detectors[2, 1].pix2world(PIXEL_SHAPE[0], 1)

        # get FOV coords of these positions (buffer to avoid any weird rounding at detector edge)
        x11, y11 = frame.get_fov_coords(ra11, dec11, x_buffer=0.1, y_buffer=0.1)
        x12, _ = frame.get_fov_coords(ra12, dec12, x_buffer=0.1, y_buffer=0.1)
        _, y21 = frame.get_fov_coords(ra21, dec21, x_buffer=0.1, y_buffer=0.1)

        # make sure distance between detectors is bigger in the y direction than the x
        assert np.abs(x11 - x12) < np.abs(
            y11 - y21
        ), "Gap between detectors is bigger in x than y - detector IDs may be transposed?"
