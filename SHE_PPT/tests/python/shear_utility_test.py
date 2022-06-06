""" @file shear_utility_test.py

    Created 14 May 2019

    Unit tests of functions in the SHE_PPT.shear_utility module
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

from copy import deepcopy

import galsim
import numpy as np
from astropy.io import fits

from SHE_PPT.constants.fits import GAIN_LABEL, SCALE_LABEL
from SHE_PPT.she_image import SHEImage
from SHE_PPT.shear_utility import (ShearEstimate, correct_for_wcs_shear_and_rotation,
                                   uncorrect_for_wcs_shear_and_rotation, )
from SHE_PPT.testing.utility import SheTestCase


class TestCase(SheTestCase):
    """ Test case class for shear utility tests
    """

    def setup_workdir(self):
        """ Set up a default galaxy stamp and PSF stamp for testing.
        """

        self._download_mdb()

        self.sky_var = 0
        self.bkg_level = 1000
        self.psf_pixel_scale = 0.02
        self.gal_pixel_scale = 0.10

        self.xs = 100
        self.ys = 100

        self.psf_xs = 250
        self.psf_ys = 250

        self.g1 = 0
        self.g2 = 0

        self.gal_ID = 4

        # Set up the galaxy profile we'll be using
        self.base_gal = galsim.Sersic(n = 1, half_light_radius = 0.5)

        # Set up the psf we'll be using and a subsampled image of it
        self.psf = galsim.Airy(lam_over_diam = 0.2)

        self.ss_psf_image = galsim.Image(self.psf_xs, self.psf_ys, scale = self.psf_pixel_scale)
        self.psf.drawImage(self.ss_psf_image, use_true_center = False)

        self.bkg_image = galsim.Image(self.xs, self.ys, scale = self.gal_pixel_scale)
        self.bkg_image += self.bkg_level

        self.psf_stamp = SHEImage(self.ss_psf_image.array.transpose())
        self.psf_stamp.add_default_header()
        self.psf_stamp.header[SCALE_LABEL] = self.ss_psf_image.scale

        # Draw the default galaxy
        self.observed_gal = galsim.Convolve([self.base_gal.shear(g1 = self.g1, g2 = self.g2), self.psf])
        self.observed_gal_image = galsim.Image(self.xs, self.ys, scale = self.gal_pixel_scale)
        self.observed_gal.drawImage(self.observed_gal_image, use_true_center = False)

        self.observed_gal_image += self.bkg_image

        self.gal_stamp = SHEImage(self.observed_gal_image.array.transpose(),
                                  mask = np.zeros_like(self.observed_gal_image.array.transpose(), dtype = np.int8),
                                  segmentation_map = self.gal_ID * np.ones_like(
                                      self.observed_gal_image.array.transpose(), dtype = np.int8),
                                  background_map = self.bkg_image.array.transpose(),
                                  noisemap = 0.0001 * np.ones_like(
                                      self.observed_gal_image.array.transpose(), dtype = float),
                                  header = fits.Header())
        self.gal_stamp.add_default_header()
        self.gal_stamp.header[SCALE_LABEL] = self.observed_gal_image.scale
        self.gal_stamp.header[GAIN_LABEL] = 1.0

        return

    def test_correct_wcs_shear(self):
        """ Tests of the calculations for correcting for a WCS shear.
        """

        wcs_shear = galsim.Shear(g1 = 0.1, g2 = 0.2)
        gal_shear = galsim.Shear(g1 = 0.5, g2 = 0.3)

        gerr = 0.3
        weight = 1 / gerr ** 2

        # Ordering is important here. Galaxy shear is in reality applied first, so it's last in addition
        tot_shear = wcs_shear + gal_shear

        # Create a ShearEstimate object for testing
        shear_estimate = ShearEstimate(g1 = tot_shear.g1,
                                       g2 = tot_shear.g2,
                                       g1_err = gerr,
                                       g2_err = gerr,
                                       weight = weight)

        init_shear_estimate = deepcopy(shear_estimate)

        # Create a mock SHEImage stamp for testing
        gs_header = galsim.FitsHeader()
        galsim_wcs = galsim.ShearWCS(shear = wcs_shear, scale = 1.0)
        galsim_wcs.writeToFitsHeader(gs_header, galsim.BoundsI(1, 1, 2, 2))

        ap_header = fits.Header(gs_header.header)
        mock_stamp = SHEImage(data = np.zeros((1, 1)), offset = np.array((0., 0.)),
                              header = ap_header)

        mock_stamp.galsim_wcs = galsim_wcs

        # Try correcting the shear estimate
        correct_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

        assert np.isclose(shear_estimate.g1, gal_shear.g1)
        assert np.isclose(shear_estimate.g2, gal_shear.g2)
        assert np.isclose(shear_estimate.g1_err, gerr)
        assert np.isclose(shear_estimate.g2_err, gerr)
        assert np.isclose(shear_estimate.g1g2_covar, 0.)
        assert np.isclose(shear_estimate.weight, weight)

        # Now test that uncorrecting also works as expected
        uncorrect_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

        assert np.isclose(shear_estimate.g1, init_shear_estimate.g1)
        assert np.isclose(shear_estimate.g2, init_shear_estimate.g2)
        assert np.isclose(shear_estimate.g1_err, init_shear_estimate.g1_err)
        assert np.isclose(shear_estimate.g2_err, init_shear_estimate.g1_err)
        assert np.isclose(shear_estimate.g1g2_covar, init_shear_estimate.g1g2_covar)
        assert np.isclose(shear_estimate.weight, init_shear_estimate.weight)

        return

    def test_correct_wcs_rotation(self):
        """ Tests of the calculations for correcting for a WCS rotation.
        """

        gerr = 0.3
        weight = 1 / gerr ** 2

        for (p2w_theta, tot_g1, tot_g2, ex_g1_err, ex_g2_err, ex_g1g2covar) in (
                (45 * galsim.degrees, 0.3, -0.5, gerr, gerr, 0.),
                (22.5 * galsim.degrees, 0.565685424949238, -0.14142135623730948, gerr, gerr, 0)):

            sin_theta = p2w_theta.sin()
            cos_theta = p2w_theta.cos()

            # Expected values are easy with a 45-degree rotation
            gal_shear = galsim.Shear(g1 = 0.5, g2 = 0.3)
            tot_shear = galsim.Shear(g1 = tot_g1, g2 = tot_g2)

            # Create a ShearEstimate object for testing
            shear_estimate = ShearEstimate(g1 = tot_shear.g1,
                                           g2 = tot_shear.g2,
                                           g1_err = gerr,
                                           g2_err = gerr,
                                           weight = weight)

            init_shear_estimate = deepcopy(shear_estimate)

            # Create a mock SHEImage stamp for testing
            gs_header = galsim.FitsHeader()
            wcs = galsim.AffineTransform(dudx = cos_theta, dudy = -sin_theta,
                                         dvdx = sin_theta, dvdy = cos_theta)
            wcs.writeToFitsHeader(gs_header, galsim.BoundsI(1, 1, 2, 2))
            ap_header = fits.Header(gs_header.header)
            mock_stamp = SHEImage(data = np.zeros((1, 1)), offset = np.array((0., 0.)),
                                  header = ap_header)

            mock_stamp.galsim_wcs = wcs

            # Try correcting the shear estimate
            correct_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

            assert np.isclose(shear_estimate.g1, gal_shear.g1)
            assert np.isclose(shear_estimate.g2, gal_shear.g2)
            assert np.isclose(shear_estimate.g1_err, ex_g1_err)
            assert np.isclose(shear_estimate.g2_err, ex_g2_err)
            assert np.isclose(shear_estimate.g1g2_covar, ex_g1g2covar)
            assert np.isclose(shear_estimate.weight, weight)

            # Now test that uncorrecting also works as expected
            uncorrect_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

            assert np.isclose(shear_estimate.g1, init_shear_estimate.g1)
            assert np.isclose(shear_estimate.g2, init_shear_estimate.g2)
            assert np.isclose(shear_estimate.g1_err, init_shear_estimate.g1_err)
            assert np.isclose(shear_estimate.g2_err, init_shear_estimate.g1_err)
            assert np.isclose(shear_estimate.g1g2_covar, init_shear_estimate.g1g2_covar)
            assert np.isclose(shear_estimate.weight, init_shear_estimate.weight)

        return

    def test_correct_wcs_shear_and_rotation(self):
        """ Tests of the calculations for correcting for a WCS with both shear and rotation.
        """

        gerr = 0.3
        weight = 1 / gerr ** 2

        wcs_shear = galsim.Shear(g1 = 0.2, g2 = 0.)
        gal_shear = galsim.Shear(g1 = 0.5, g2 = 0.3)

        p2w_theta = 45 * galsim.degrees

        sin_theta = p2w_theta.sin()
        cos_theta = p2w_theta.cos()

        gal_shear_rotated = galsim.Shear(g1 = 0.3, g2 = -0.5)

        shear_matrix = np.array([[1 + wcs_shear.g1, wcs_shear.g2],
                                 [wcs_shear.g2, 1 - wcs_shear.g1]])
        rotation_matrix = np.array([[cos_theta, -sin_theta],
                                    [sin_theta, cos_theta]])

        transform_matrix = 1.0 / np.sqrt(1 - wcs_shear.g1 ** 2 - wcs_shear.g2 ** 2) * shear_matrix @ rotation_matrix

        # Ordering is important here. Galaxy shear is in reality applied first, so it's last in addition
        tot_shear = wcs_shear + gal_shear_rotated

        # Create a ShearEstimate object for testing
        shear_estimate = ShearEstimate(g1 = tot_shear.g1,
                                       g2 = tot_shear.g2,
                                       g1_err = gerr,
                                       g2_err = gerr,
                                       weight = weight)

        init_shear_estimate = deepcopy(shear_estimate)

        # Create a mock SHEImage stamp for testing
        gs_header = galsim.FitsHeader()
        wcs = galsim.AffineTransform(dudx = transform_matrix[0, 0], dudy = transform_matrix[0, 1],
                                     dvdx = transform_matrix[1, 0], dvdy = transform_matrix[1, 1])
        wcs.writeToFitsHeader(gs_header, galsim.BoundsI(1, 1, 2, 2))
        ap_header = fits.Header(gs_header.header)
        mock_stamp = SHEImage(data = np.zeros((1, 1)), offset = np.array((0., 0.)),
                              header = ap_header)

        mock_stamp.galsim_wcs = wcs

        # Try correcting the shear estimate
        correct_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

        assert np.isclose(shear_estimate.g1, gal_shear.g1)
        assert np.isclose(shear_estimate.g2, gal_shear.g2)
        assert np.isclose(shear_estimate.g1_err, gerr)
        assert np.isclose(shear_estimate.g2_err, gerr)
        assert np.isclose(shear_estimate.g1g2_covar, 0.)
        assert np.isclose(shear_estimate.weight, weight)

        # Now test that uncorrecting also works as expected
        uncorrect_for_wcs_shear_and_rotation(shear_estimate, mock_stamp)

        assert np.isclose(shear_estimate.g1, init_shear_estimate.g1)
        assert np.isclose(shear_estimate.g2, init_shear_estimate.g2)
        assert np.isclose(shear_estimate.g1_err, init_shear_estimate.g1_err)
        assert np.isclose(shear_estimate.g2_err, init_shear_estimate.g1_err)
        assert np.isclose(shear_estimate.g1g2_covar, init_shear_estimate.g1g2_covar)
        assert np.isclose(shear_estimate.weight, init_shear_estimate.weight)

        return
