""" @file gain.py

    Created 22 Mar 2017

    Functions to handle needed conversions and calculations for noise
    in simulated images.
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

from SHE_PPT.gain import get_ADU_from_count, get_count_from_ADU

def get_sky_level_ADU_per_pixel(sky_level_ADU_per_sq_arcsec,
                                pixel_scale):
    """ Calculate the sky level in units of ADU per pixel from the sky level per square arcsecond.

        @param sky_level_ADU_per_sq_arcsec The sky level in units of ADU/arcsec^2
        @param pixel_scale The pixel scale in units of arcsec/pixel

        @return The sky level in units of ADU/pixel
    """
    
    sky_level_ADU_per_pixel = sky_level_ADU_per_sq_arcsec * pixel_scale**2
    
    return sky_level_ADU_per_pixel

def get_sky_level_count_per_pixel(sky_level_ADU_per_sq_arcsec,
                                  pixel_scale,
                                  gain):
    """ Calculate the sky level in units of count per pixel from the sky level per square arcsecond.

        @param sky_level_ADU_per_sq_arcsec The sky level in units of ADU/arcsec^2
        @param pixel_scale The pixel scale in units of arcsec/pixel
        @param gain The gain in units of e-/ADU

        @return The sky level in units of e-/pixel
    """
    
    sky_level_ADU_per_pixel = get_sky_level_ADU_per_pixel(sky_level_ADU_per_sq_arcsec,pixel_scale)
    sky_level_count_per_pixel = get_count_from_ADU(sky_level_ADU_per_pixel,gain)
    
    return sky_level_count_per_pixel

def get_count_lambda_per_pixel(pixel_value_ADU,
                               sky_level_ADU_per_sq_arcsec,
                               pixel_scale,
                               gain):
    """ Calculate the lambda of the Poisson distribution for a pixel's noise.

        @param pixel_value The expected value of a pixel in ADU. Can be a scalar or array
        @param sky_level_ADU_per_sq_arcsec The sky level in units of ADU/arcsec^2
        @param pixel_scale The pixel scale in units of arcsec/pixel
        @param gain The gain in units of e-/ADU

        @return The lambda of the Poisson distribution in units of e-
    """
    
    pixel_value_count = get_count_from_ADU(pixel_value_ADU, gain)
    
    sky_level_count_per_pixel = get_sky_level_count_per_pixel(sky_level_ADU_per_sq_arcsec,
                                                              pixel_scale, gain)
    
    count_lambda = pixel_value_count + sky_level_count_per_pixel
    
    return count_lambda

def get_read_noise_ADU_per_pixel(read_noise_count,
                                 gain):
    """ Calculate the read noise per pixel in units of ADU

        @param read_noise_count The read noise in e-/pixel
        @param gain The gain in units of e-/ADU

        @return The read noise per pixel in units of ADU
    """
    
    read_noise_ADU_per_pixel = get_ADU_from_count(read_noise_count, gain)
    
    return read_noise_ADU_per_pixel

def get_var_ADU_per_pixel(pixel_value_ADU,
                          sky_level_ADU_per_sq_arcsec,
                          read_noise_count,
                          pixel_scale,
                          gain):
    """ Calculate the sigma for Gaussian-like noise in units of ADU per pixel.

        @param pixel_value The expected value of a pixel in ADU. Can be a scalar or array
        @param sky_level_ADU_per_sq_arcsec The sky level in units of ADU/arcsec^2
        @param read_noise_count The read noise in e-/pixel
        @param pixel_scale The pixel scale in units of arcsec/pixel
        @param gain The gain in units of e-/ADU

        @return The sigma of the total noise in units of ADU per pixel
    """
    
    pois_count_lambda = get_count_lambda_per_pixel(pixel_value_ADU,
                                              sky_level_ADU_per_sq_arcsec, pixel_scale, gain)
    pois_ADU_var = get_ADU_from_count(get_ADU_from_count(pois_count_lambda, gain), gain) # Apply twice since it's squared
    
    read_noise_ADU_sigma = get_read_noise_ADU_per_pixel(read_noise_count, gain)
    
    total_var = pois_ADU_var + read_noise_ADU_sigma**2
    
    return total_var