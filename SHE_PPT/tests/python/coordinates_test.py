""" @file coordinates_test.py

    Created 26 Jan 2022

    Tests of functions in the 'coordinates' module.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2022-01-27"

from astropy.wcs import WCS
import numpy as np
from numpy.testing import assert_almost_equal
import pytest
from scipy.spatial.distance import pdist

from SHE_PPT.coordinates import (
    get_distance_matrix,
    get_subregion,
    haversine_metric,
    haversine_metric_deg,
    reproject_to_equator,
    skycoords_in_wcs,
)
from SHE_PPT.testing.utility import SheTestCase


class Test_coordinates(SheTestCase):
    def test_haversine_metric(self):
        """Generates many pairs of random points on a sphere and checks that the distances between them are
        calculated correctly"""

        # alternate but equivalent metric that works via dot products. Used to verify the haversine metric
        def test_metric(lon0, lat0, lon1, lat1):
            # convert lon and lat coords to Cartesian on a unit sphere
            x0 = np.cos(lat0) * np.cos(lon0)
            y0 = np.cos(lat0) * np.sin(lon0)
            z0 = np.sin(lat0)

            x1 = np.cos(lat1) * np.cos(lon1)
            y1 = np.cos(lat1) * np.sin(lon1)
            z1 = np.sin(lat1)

            # a.b = |a||b|cos(theta) -> theta = acos(a.b/|a||b|)

            # dot the two vectors together
            dot = x0 * x1 + y0 * y1 + z0 * z1

            # Sometimes due to rounding errors |dot| can end out > 1 if the separation of the points is zero
            # This causes np.arccos to fail, so correcting here
            # Ironically, the haversine metric doesn't have this problem!
            if dot > 1.0:
                dot = 1.0
            if dot < -1.0:
                dot = -1.0

            return np.arccos(dot)

        nsamples = 100

        # test nsamples randomly chosen pairs of points on the celestial sphere
        for i in range(nsamples):
            # get random pairs of lat/lon points
            lat0, lat1 = (np.random.random(2) - 0.5) * np.pi
            lon0, lon1 = (np.random.random(2) * 2) * np.pi

            # measure distance between them with the two methods
            d_hav = haversine_metric(lon0, lat0, lon1, lat1)
            d_alt = test_metric(lon0, lat0, lon1, lat1)

            assert_almost_equal(d_hav, d_alt)

            # test with order reversed (should give the same answer)
            d_hav = haversine_metric(lon1, lat1, lon0, lat0)
            assert_almost_equal(d_hav, d_alt)

        # test nsamples randomly chosen pairs of points with zero separation
        for i in range(nsamples):
            # get random pairs of lat/lon points
            lat0 = lat1 = (np.random.random() - 0.5) * np.pi
            lon0 = lon1 = (np.random.random() * 2) * np.pi

            # measure distance between them with the two methods
            d_hav = haversine_metric(lon0, lat0, lon1, lat1)
            d_alt = test_metric(lon0, lat0, lon1, lat1)

            assert_almost_equal(d_hav, d_alt)

        # test nsamples randomly chosen pairs of points antipodal WRT each other
        for i in range(nsamples):
            # get random lat/lon points
            lat0 = (np.random.random() - 0.5) * np.pi
            lon0 = (np.random.random() * 2) * np.pi

            # set the second point as an antipode
            lat1 = -1.0 * lat0
            lon1 = (lon0 + np.pi) % (2 * np.pi)

            # measure distance between them with the two methods
            d_hav = haversine_metric(lon0, lat0, lon1, lat1)
            d_alt = test_metric(lon0, lat0, lon1, lat1)

            assert_almost_equal(d_hav, d_alt)

            # test with order reversed (should give the same answer)
            d_hav = haversine_metric(lon1, lat1, lon0, lat0)
            assert_almost_equal(d_hav, d_alt)

            # make sure the distance between the points is pi radians as expected
            assert_almost_equal(d_hav, np.pi)

        # test nsamples randomly chosen pairs of points with one of the points at the pole
        for i in range(nsamples):
            # get random pairs of lat/lon points, one of which is at one of the two poles
            lat0, lat1 = ((-1) ** np.random.choice(2)) * np.pi / 2, (np.random.random() - 0.5) * np.pi
            lon0, lon1 = (np.random.random(2) * 2) * np.pi

            # measure distance between them with the two methods
            d_hav = haversine_metric(lon0, lat0, lon1, lat1)
            d_alt = test_metric(lon0, lat0, lon1, lat1)

            assert_almost_equal(d_hav, d_alt)

            # test with order reversed (should give the same answer)
            d_hav = haversine_metric(lon1, lat1, lon0, lat0)
            assert_almost_equal(d_hav, d_alt)

    def test_distance_matrix(self):
        """Ensures get_distance_matrix works correctly by comparing its results to scipy.spatial.distance.pdist.
        This also incidentally tests SHE_PPT.coodinates.euclidean_metric against scipy.spatial.distance.pdist's
        euclidean metric"""

        # generate n random points in 2D
        n = 1000

        x = np.random.random(n)
        y = np.random.random(n)

        # get distance matrix using the PPT code we're testing
        dists = get_distance_matrix(x, y)

        # put the points into the form required by pdist
        A = np.zeros((n, 2))
        A[:, 0] = x[:]
        A[:, 1] = y[:]

        # get distance matrix using scipy.spatial.distance.pdist
        dists_ref = pdist(A)

        # Ensure they are equal (within a tolerance)
        assert np.allclose(dists, dists_ref)

    def test_reproject_to_equator(self):
        """Tests reproject_to_equator by generating many sets of points and reprojecting them, ensuring
        the reprojection conserves distances between points, and repositions the points correctly"""

        # checks if a set of points has been reprojected correctly
        def check_reprojection(ras, decs):
            # get the distances between all the original points
            original_dists = get_distance_matrix(ras, decs, metric=haversine_metric_deg)

            # reproject points
            new_ras, new_decs = reproject_to_equator(ras, decs)

            # get the distances between all reprojected points
            new_dists = get_distance_matrix(new_ras, new_decs, metric=haversine_metric_deg)

            # ensure the distances aren't altered by the reprojection
            assert np.allclose(original_dists, new_dists)

            # check the centre of mass of the reprojected points is close to (0,0)
            xc = new_ras.mean()
            yc = new_decs.mean()

            assert np.isclose(0.0, xc, rtol=0.001, atol=0.001)
            assert np.isclose(0.0, yc, rtol=0.001, atol=0.001)

        n = 100

        # Check accuracy for points not at the poles (|dec| < 89 degrees)
        # generate a square of n points about (0,0) with width of 0.5  (approx size and shape of an observation)
        # place this square anywhere between +/- 85 degrees declination, any right ascension
        for i in range(1000):
            x = (np.random.random(n) - 0.5) * 0.5
            y = (np.random.random(n) - 0.5) * 0.5

            # rotate the square by random angle theta
            theta = np.random.random() * np.pi / 4
            x, y = x * np.cos(theta) - y * np.sin(theta), x * np.sin(theta) + y * np.cos(theta)

            # shift these points by a random value
            x += np.random.random() * 360.0
            y += (np.random.random() - 0.5) * 178.0

            # treat these shifted x/y coordinates as right ascensions and declinations (in degrees)
            ras = x
            decs = y

            # make sure ras are in the range [0:360)
            ras = ras % 360

            check_reprojection(ras, decs)

        # check accuracy for points near-ish/at the celestial poles (|dec| > 89 degrees)
        # generate a square of n points about (0,0) with width of 0.5  (approx size and shape of an observation)
        # place this square near the pole at a random position (anywhere within 1 degree of the pole)
        for i in range(1000):
            x = (np.random.random(n) - 0.5) * 0.5
            y = (np.random.random(n) - 0.5) * 0.5

            # rotate the square by random angle theta
            theta = np.random.random() * np.pi / 4
            x, y = x * np.cos(theta) - y * np.sin(theta), x * np.sin(theta) + y * np.cos(theta)

            # place the square somewhere at random within a circle of radius 5
            r = np.random.random()
            theta = np.random.random() * 2 * np.pi
            x += np.cos(theta) * r
            y += np.sin(theta) * r

            # convert x and y into ra and dec
            decs = 90 - np.sqrt(x * x + y * y)
            # randomly pick northern or southern hemisphere
            decs *= (-1) ** np.random.choice(2)
            ras = np.arctan2(y, x) * 180.0 / np.pi

            # make sure ras are in the range [0:360)
            ras = ras % 360

            check_reprojection(ras, decs)

    def test_get_subregion(self):
        """Checks that get_subregion correctly extracts a subregion"""

        n = 10000

        # generate n randomly distributed points between 0 and 1 in 2D
        x = np.random.random(n)
        y = np.random.random(n)
        flag = np.zeros(n, np.int64)

        xmin, xmax = 0.3, 0.7
        ymin, ymax = 0.1, 0.9

        x_s, y_s, indices = get_subregion(x, y, xmin, xmax, ymin, ymax)

        # identify objects in x and y that are in x_s, y_s
        flag[indices] = 1

        # make sure that the indices returned are correct
        for i in range(n):
            if x[i] >= xmin and x[i] < xmax and y[i] >= ymin and y[i] < ymax:
                assert flag[i] == 1
            else:
                assert flag[i] == 0

        # make sure all points extracted are within the sub region
        for i in range(len(x_s)):
            if x_s[i] >= xmin and x_s[i] < xmax and y_s[i] >= ymin and y_s[i] < ymax:
                assert True
            else:
                assert False

    @pytest.mark.parametrize("ra", np.arange(0.0, 360.0, 90.0))
    @pytest.mark.parametrize("dec", np.arange(-90.0, 90.0, 45.0))
    def test_wcs_query(self, ra, dec):
        pixel_scale = 0.1 / 3600.0
        nx = 100
        ny = 150
        n_objs = 1000

        wcs = WCS(naxis=2)
        # use rectangle to avoid bugs undetector due to symmetry
        # this follows the C-standard, so it is y then x
        wcs.array_shape = [ny, nx]
        # note this starts counting from 1
        # this follows the Fortran-standard, so it is x then y
        wcs.wcs.crpix = [nx / 2, ny / 2]
        wcs.wcs.crval = [ra, dec]
        wcs.wcs.cd = np.identity(2) * pixel_scale
        # RA decreases with increasing pixel number
        wcs.wcs.cd[0, 0] *= -1
        wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]

        # generate a range of random points *within* the footprint area
        # this follows the C-standard, so it is y then x
        # Note that:
        # wcs.array_shape[0] = wcs.pixel_shape[1]
        # wcs.array_shape[1] = wcs.pixel_shape[0]
        pix_y_in = np.random.random(n_objs) * wcs.array_shape[0]
        pix_x_in = np.random.random(n_objs) * wcs.array_shape[1]
        # this follows the Fortran-standard, so it is x then y
        skycoords_in = wcs.pixel_to_world(pix_x_in, pix_y_in)

        # generate a range of points *immediately outside* the footprint area
        pix_x_out = np.array([-1, -1, -1, -1, 101, 101, 101, 101, -1, 1, 99, 101, -1, 1, 99, 101])
        pix_y_out = np.array([-1, 1, 149, 151, -1, 1, 149, 151, -1, -1, -1, -1, 151, 151, 151, 151])
        # this follows the Fortran-standard, so it is x then y
        skycoord_out = wcs.pixel_to_world(pix_x_out, pix_y_out)

        s_in = skycoords_in_wcs(skycoords_in, wcs)
        s_out = skycoords_in_wcs(skycoord_out, wcs)

        assert np.sum(s_in) == n_objs
        assert np.sum(s_out) == 0
