""" @file noise_test.py

    Created 6 July 2017

    Tests of functions dealing with noise calculations.
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

import unittest
from numpy.testing import assert_almost_equal
from SHE_GST_GalaxyImageGeneration.noise import (get_sky_level_ADU_per_pixel, get_sky_level_count_per_pixel,
                                                 get_count_lambda_per_pixel, get_read_noise_ADU_per_pixel,
                                                 get_var_ADU_per_pixel)

class NoiseTestCase(unittest.TestCase):
    
    def setUp(self):
        
        self.pixel_scale = 0.1
        self.gain = 2.5
        self.pixel_value_ADU = 500
        
        self.sky_level_ADU_per_sq_arcsec = 100000
        self.sky_level_ADU_per_pixel = 1000
        self.sky_level_count_per_pixel = 2500
        
        self.read_noise_count_per_pixel = 10
        self.read_noise_ADU_per_pixel = 4
        
        self.count_lambda_per_pixel = 3750
        self.var_ADU_per_pixel = 616

    def test_get_sky_level_ADU_per_pixel(self):
        
        sky_level_ADU_per_pixel = get_sky_level_ADU_per_pixel(self.sky_level_ADU_per_sq_arcsec,
                                                              self.pixel_scale)
        
        assert_almost_equal(sky_level_ADU_per_pixel, self.sky_level_ADU_per_pixel)

    def test_get_sky_level_count_per_pixel(self):
        
        sky_level_count_per_pixel = get_sky_level_count_per_pixel(self.sky_level_ADU_per_sq_arcsec,
                                                                  self.pixel_scale,
                                                                  self.gain)
        
        assert_almost_equal(sky_level_count_per_pixel, self.sky_level_count_per_pixel)

    def test_get_count_lambda_per_pixel(self):
        
        count_lambda_per_pixel = get_count_lambda_per_pixel(self.pixel_value_ADU,
                                                            self.sky_level_ADU_per_sq_arcsec,
                                                            self.pixel_scale,
                                                            self.gain)
        
        assert_almost_equal(count_lambda_per_pixel, self.count_lambda_per_pixel)

    def get_read_noise_ADU_per_pixel(self):
        
        read_noise_ADU_per_pixel = get_count_lambda_per_pixel(self.read_noise_count_per_pixel,
                                                              self.gain)
        
        assert_almost_equal(read_noise_ADU_per_pixel, self.read_noise_ADU_per_pixel)
        
    def test_get_var_ADU_per_pixel(self):
        
        var_ADU_per_pixel = get_var_ADU_per_pixel(self.pixel_value_ADU,
                                                  self.sky_level_ADU_per_sq_arcsec,
                                                  self.read_noise_count_per_pixel,
                                                  self.pixel_scale,
                                                  self.gain)
        
        assert_almost_equal(var_ADU_per_pixel, self.var_ADU_per_pixel)
        
