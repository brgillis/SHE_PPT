"""
    @file get_I_from_SN.py

    Created 23 Jul 2015

    Contains function "get_I_from_SN" to estimate the required intensity of
    a galaxy to provide a given signal-to-noise.
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

import numpy as np


def get_I_from_SN(galaxy_SN             ,
             galaxy_stddev_arcsec  ,
             psf_stddev_arcsec     ,
             sky_level_subtracted  ,
             sky_level_unsubtracted,
             read_noise            ,
             pixel_scale           ,
             gain):
    """
        @brief
            Estimates galaxy intensity (in ADU) from signal-to-noise ratio.

        @details
            The definition used here is a simplified tophat model, with the tophat containing
           ~50% of the light for a circular galaxy and PSF. This definition is used simply
           because it's easy to analytically invert.

        @param galaxy_SN
            The signal-to-noise ratio of the galaxy.
        @param galaxy_stddev_arcsec
            The standard deviation of the (Gaussian) galaxy in units of arcsec.
        @param psf_stddev_arcsec
            The standard deviation of the (Gaussian) psf in units of arcsec.
        @param sky_level_subtracted
            The sky background level which has been previously subtracted off of the image, in units
            of ADU/arcsec^2
        @param sky_level_unsubtracted
            The sky background level which has not been previously subtracted off of the image, in units
            of ADU/arcsec^2
        @param read_noise
            The read noise of the observation, in units of e-/pixel
        @param pixel_scale
            The pixel scale of the image, in units of arcsec/pixel
        @param gain
            The gain of the observation, in units of e-/ADU

        @returns I
            The galaxy intensity in ADU
    """

    # Estimate the half-light radius of the galaxy (using the magic number 0.674490, which represents the
    # sigma for a Gaussian which contains half the distribution), and use it to calculate the area within
    # the half-light aperture in arcsec
    size_of_gal = np.pi * 0.674490 * ((galaxy_stddev_arcsec) ** 2 + (psf_stddev_arcsec) ** 2)

    # Calculate the sky noise and read noise in the half-light aperture, remembering that noise scales with
    # the sqrt of area.

    # Sky level is given initially in ADU/arcsec^2. So we convert to counts by multiplying by gain, then
    # take the sqrt of counts to get noise (assuming it's Poisson). Then we scale by sqrt(size_of_gal).
    sky_noise_behind_galaxy = np.sqrt((sky_level_subtracted + sky_level_unsubtracted) * gain * size_of_gal)

    # Read noise is given initially in counts/pixel. So we convert to counts per arcsec (using just pixel_scale,
    # not pixel_scale^2 since it scales with sqrt(area), and then scale by sqrt(size_of_gal)
    read_noise_behind_galaxy = read_noise * np.sqrt(size_of_gal) / pixel_scale

    # Total noise is sum in quadrature of the two components
    background_noise = np.sqrt(sky_noise_behind_galaxy ** 2 + read_noise_behind_galaxy ** 2)

    # The galaxy's S/N is calculated from both its own Poisson noise and the background noise within its
    # half-light aperture. This can be analytically inverted to give the expression below.
    I = galaxy_SN * (galaxy_SN + np.sqrt(4 * background_noise ** 2 + galaxy_SN ** 2))

    return I
