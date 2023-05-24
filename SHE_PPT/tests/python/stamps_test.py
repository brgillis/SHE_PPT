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
:file: tests/python/stamps_test.py

:date: 08/11/22
:author: Gordon Gibb
"""

import pytest
import os

from astropy.table import Table
from astropy.wcs import WCS
import numpy as np


from SHE_PPT.she_io.stamps import extract_exposure_stamp, Stamp, wcs_with_buffer
from SHE_PPT.she_io.vis_exposures import VisExposureAstropyFITS

# NOTE the file conftest.py contains or imports the pytest fixtures used by this test


class Teststamps(object):
    def test_extract_stamps(self, workdir, input_fits):
        """Tests extract_stamps"""

        # get the input FITS data, and their corresponding VisExposure object
        det, wgt, bkg, mer, _, _, seg = input_fits

        det_file = os.path.join(workdir, "data", det)
        wgt_file = os.path.join(workdir, "data", wgt)
        bkg_file = os.path.join(workdir, "data", bkg)
        seg_file = os.path.join(workdir, "data", seg)
        mer_file = os.path.join(workdir, "data", mer)

        mer_t = Table.read(mer_file)

        exp = VisExposureAstropyFITS(det_file, bkg_file, wgt_file, seg_file)

        # We assume astropy.nddata.utils.Cutout2D works, so we simply check that we can extract a stamp
        # from a valid ra/dec, and that we cannot extract a stamp from an invalid ra/dec

        ra = mer_t[0]["RIGHT_ASCENSION"]
        dec = mer_t[0]["DECLINATION"]

        stamp = extract_exposure_stamp(exp, ra, dec, size=200)

        assert type(stamp) is Stamp, "Extracted stamp is an unexpected type"

        # select an antipodal point on the sky as an invalid ra/dec (as this is guaranteed not to be in the observation)

        bad_ra = (ra + 180) % 360
        bad_dec = -dec

        stamp = extract_exposure_stamp(exp, bad_ra, bad_dec, size=200)

        assert stamp is None, "Extracted stamp from invalid coordinates, but the returned stamp was not None"

    def test_wcs_with_buffer(self):
        """Tests wcs_with_buffer"""

        NX = 100
        NY = 200
        PIXELSIZE = 1.0 / 3600.0

        BUFSIZE = 3

        # create WCS (Use Airy projection - arbitrary decision, we just want something in valid sky coordinates!)
        wcs = WCS(naxis=2)
        wcs.wcs.crpix = (NX // 2, NY // 2)
        wcs.wcs.crval = (0.0, 0.0)
        wcs.wcs.cdelt = (PIXELSIZE, PIXELSIZE)
        wcs.wcs.ctype = ("RA---AIR", "DEC--AIR")
        wcs.pixel_shape = (NX, NY)

        # wcs.footprint_contains assumes the pixel is from i -> i+1, such that the centre of the pixel is at i+0.5
        # This means the pixel values contained within a dimension range from 0:N

        # points outwith and within +/-buffsize at the ends of the image
        # p (-buffer) p (0) p (buffer) p ... p (N-buffer) p (N) p (N+buffer) p
        x_points = [
            -2 * BUFSIZE,
            -BUFSIZE / 2,
            BUFSIZE / 2,
            2 * BUFSIZE,
            NX - 2 * BUFSIZE,
            NX - BUFSIZE / 2,
            NX + BUFSIZE / 2,
            NX + 2 * BUFSIZE,
        ]
        y_points = [
            -2 * BUFSIZE,
            -BUFSIZE / 2,
            BUFSIZE / 2,
            2 * BUFSIZE,
            NY - 2 * BUFSIZE,
            NY - BUFSIZE / 2,
            NY + BUFSIZE / 2,
            NY + 2 * BUFSIZE,
        ]

        xs, ys = np.meshgrid(x_points, y_points)
        xs = xs.ravel()
        ys = ys.ravel()

        # convert these to sky coorinates
        skycoords = wcs.pixel_to_world(xs, ys)

        # a set of x_buffer and y_buffer permutations to test (tests positive, negative and zero x and y buffers)
        buffers = [
            (0, 0),
            (BUFSIZE, 0),
            (0, BUFSIZE),
            (BUFSIZE, BUFSIZE),
            (-BUFSIZE, 0),
            (0, -BUFSIZE),
            (-BUFSIZE, -BUFSIZE),
        ]

        x_buffers, y_buffers = zip(*buffers)

        # loop over all buffer permutations
        for x_buffer, y_buffer in zip(x_buffers, y_buffers):

            # get WCS with buffers
            buffered_wcs = wcs_with_buffer(wcs, x_buffer, y_buffer)

            # Calculate whether a pixel should be contained within this WCS
            x_cond = [x_buffer <= x < NX - x_buffer for x in xs]
            y_cond = [y_buffer <= y < NY - y_buffer for y in ys]
            should_contains = [xc and yc for xc, yc in zip(x_cond, y_cond)]

            # Ask the WCS whether these pixels are contained by it or not
            contains = buffered_wcs.footprint_contains(skycoords)

            # Verify this is correct - with helpful (for debugging) assertion messages if a failure occurs
            for i in range(len(skycoords)):
                contain = contains[i]
                should_contain = should_contains[i]
                x = xs[i]
                y = ys[i]
                if should_contain:
                    msg = "Point (%d,%d) should be in detector with x_buffer = %d and y_buffer = %d but is not"
                else:
                    msg = "Point (%d,%d) should not be in detector with x_buffer = %d and y_buffer = %d but is"

                assert contain == should_contain, msg % (x, y, x_buffer, y_buffer)

        # make sure ValueError is thrown if either x_buffer or y_buffer are passed in as floats
        with pytest.raises(ValueError):
            wcs_with_buffer(wcs, x_buffer=1.5)

        with pytest.raises(ValueError):
            wcs_with_buffer(wcs, y_buffer=1.5)

        with pytest.raises(ValueError):
            wcs_with_buffer(wcs, x_buffer=1.5, y_buffer=1.5)
