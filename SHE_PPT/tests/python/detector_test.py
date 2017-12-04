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
File: tests/python/detector_test.py

Created on: 8 Nov, 2017
"""



import pytest
import numpy as np
import os
import logging

from SHE_PPT.detector import *

logging.basicConfig(level=logging.DEBUG)

class Test_mask():
    
    def test_get_id_string(self):
        
        assert get_id_string(3,4) == "CCDID 3-4"
        
        with pytest.raises(TypeError):
            get_id_string(3.1,4)
        
        with pytest.raises(TypeError):
            get_id_string(3,"foo")
            
        with pytest.raises(ValueError):
            get_id_string(0,4)
            
        with pytest.raises(ValueError):
            get_id_string(1,7)
        
        pass
    
    def test_get_detector_xy(self):
        
        assert get_detector_xy("CCDID 3-4") == (3,4)
        
        assert get_detector_xy("CCDID 3-4.SCI") == (3,4)
        
        with pytest.raises(TypeError):
            get_detector_xy(3)
        
        with pytest.raises(ValueError):
            get_detector_xy("foo")
            
        pass
    
    def test_detector_int_to_xy(self):
        
        assert detector_int_to_xy(10) == (5,2)
        
        with pytest.raises(TypeError):
            detector_int_to_xy("10")
        
        with pytest.raises(ValueError):
            detector_int_to_xy(-1)
        
        with pytest.raises(ValueError):
            detector_int_to_xy(36)
            
        pass
    
    def test_detector_xy_to_int(self):
        
        assert detector_xy_to_int(5,2) == 10
        
        with pytest.raises(TypeError):
            detector_xy_to_int(1,"10")
        
        with pytest.raises(TypeError):
            detector_xy_to_int("10",1)
        
        with pytest.raises(ValueError):
            detector_xy_to_int(0,1)
        
        with pytest.raises(ValueError):
            detector_xy_to_int(1,7)
            
        pass
    
    def test_resolve_detector_xy(self):
        
        assert resolve_detector_xy("CCDID 5-3") == (5,3)
        assert resolve_detector_xy(16) == (5,3)
        assert resolve_detector_xy((5,3)) == (5,3)
        
        with pytest.raises(TypeError):
            resolve_detector_xy(3.1)
        
        with pytest.raises(TypeError):
            resolve_detector_xy((1,2,3))
            
        pass
        

