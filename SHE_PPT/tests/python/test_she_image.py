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
#"""This script gives a small demo of the image object.

"""
File: tests/python/test_she_image.py

Created on: 08/18/17
"""

from __future__ import division, print_function
from future_builtins import *

import pytest
import SHE_PPT.she_image

import numpy as np
import os


class Test_she_image():

    def test_init(self):
        """We create a SHEImage from a random data-array, and let the code make a mask and a noisemap"""
         
        w = 50 # width
        h = 10 # height
        
        array = np.random.randn(w*h).reshape((w, h))
       
        img = SHE_PPT.she_image.SHEImage(array)
        
        assert img.shape == (w, h)
        assert img.data.shape == (w, h)
        assert img.mask.shape == (w, h)
        assert img.noisemap.shape == (w, h)
    
        # Accessing some data, checking bounds
        img.data[w-1, h-1] = 0.0
        
    @classmethod
    def setup_class(cls):
        cls.testfilepath = "test_SHEImage.fits"

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.testfilepath):
            os.remove(cls.testfilepath)
    
    
    def test_fits_read_write(self):
        """We save a small SHEImage, read it again, compare both, and delete the created file"""
        
        size = 50
        data_array = np.random.randn(size**2).reshape((size, size))
        
        mask_array = None
        noisemap_array = 1.0 + 0.01*np.random.randn(size**2).reshape((size, size))
        img = SHE_PPT.she_image.SHEImage(data_array, mask_array, noisemap_array)
        img.mask[0:10,:]=True # Just to have something non-trivial

        img.write_to_fits(self.testfilepath, clobber=False)
        
        rimg = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepath)
        
        assert np.allclose(img.data, rimg.data)
        assert np.allclose(img.mask, rimg.mask)
        assert np.allclose(img.noisemap, rimg.noisemap)
        
    def test_extract_stamp(self):
        """We test that the stamp extraction works"""
        
        size = 64
        array = np.random.randn(size**2).reshape((size, size))
        array[0:32,0:32] = 1.0e15 # bottom-left stamp is high and constant
        img = SHE_PPT.she_image.SHEImage(array)
        img.mask[32:64,:]=True
        
        
        # Testing extracted shape and extracted mask
        eimg = img.extract_stamp(16.4, 15.6, 32)
        assert eimg.shape == (32, 32)
        assert np.sum(eimg.mask) == 0 # Nothing should be masked
        assert np.std(eimg.data) < 1.0e-10
        
        eimg = img.extract_stamp(32+16.4, 32+15.6, 32)
        assert eimg.shape == (32, 32) 
        assert np.sum(eimg.mask) == 32*32 # This one is fully masked  
        assert np.std(eimg.data) > 1.0e-10
        
        
        
        
        
        
        
        

