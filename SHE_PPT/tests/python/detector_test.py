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

from __future__ import division, print_function
from future_builtins import *

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
    
    def test_id_strings(self):
        
        assert np.shape(id_strings) == (6,6)
        
        for x in range(6):
            for y in range(6):
                assert id_strings[x,y] == "CCDID $X-$Y".replace("$X",str(x+1)).replace("$Y",str(y+1))
        

