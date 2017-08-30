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

    @classmethod
    def setup_class(cls):
        
        # A filename for testing the file-saving:
        cls.testfilepath = "test_SHEImage.fits" # Will be deleted by teardown_class()
        
        # A SHEImage object to play with
        cls.w = 50
        cls.h = 20
        array = np.random.randn(cls.w*cls.h).reshape((cls.w, cls.h))
        cls.img = SHE_PPT.she_image.SHEImage(array)

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.testfilepath):
            os.remove(cls.testfilepath)

    
       
    def test_init(self):
        """Test that the object created by setup_class is as expected"""
         
        assert self.img.shape == (self.w, self.h)
        assert self.img.data.shape == (self.w, self.h)
        assert self.img.mask.shape == (self.w, self.h)
        assert self.img.noisemap.shape == (self.w, self.h)
    
       
    
    def test_fits_read_write(self):
        """We save the small SHEImage, read it again, and compare both versions"""
        
        # To have a non-trivial image, we tweak it a bit:
        self.img.noisemap = 1.0 + 0.01*np.random.randn(self.w*self.h).reshape((self.w, self.h))
        self.img.mask[0:10,:]=True

        self.img.write_to_fits(self.testfilepath, clobber=False)
        
        rimg = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepath)
        
        assert np.allclose(self.img.data, rimg.data)
        assert np.allclose(self.img.mask, rimg.mask)
        assert np.allclose(self.img.noisemap, rimg.noisemap)
    
    
    
    def test_extracted_stamp_is_view(self):
        """Checks that the extracted stamp is a view, not a copy"""
        
        stamp = self.img.extract_stamp(10.0, 10.0, 5)
        stamp.data[0,0] = -50.0
    
    def test_extract_stamp_not_square(self):
        
        stamp = self.img.extract_stamp(10.0, 10.0, 5)
        assert stamp.shape == (5, 5)
        stamp = self.img.extract_stamp(10.0, 10.0, 4, 6)
        assert stamp.shape == (4, 6)
        
    
    def test_extract_stamp_indexconvs(self):
        """Test the effect of different indexconvs"""
        
        bottomleftpixel_numpy = self.img.extract_stamp(0.5, 0.5, 1)
        bottomleftpixel_sex = self.img.extract_stamp(1.0, 1.0, 1, indexconv="sextractor")
        assert bottomleftpixel_numpy.data == bottomleftpixel_sex.data
        
        # This should fail (it's out of bounds)
        with pytest.raises(Exception):
            bottomleftpixel_sex = self.img.extract_stamp(0.5, 0.5, 1, indexconv="sextractor")
        
        
        
    def test_extract_stamp(self):
        """We test that the stamp extraction"""
        
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
        
        
        
        
        
        
        
        

