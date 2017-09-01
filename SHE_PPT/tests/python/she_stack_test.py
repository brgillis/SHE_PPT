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
File: tests/python/she_stack_test.py

Created on: 09/01/17
Author: user
"""

from __future__ import division, print_function
from future_builtins import *

import py.test

import numpy as np
from SHE_PPT.she_stack import SHEStack
from SHE_PPT.she_image import SHEImage
from SHE_PPT.detections_table_format import initialise_detections_table


class Testshe_stack(object):
    
    def test_init(self):
        
        
        data_image = SHEImage(np.random.randn(100).reshape(10,10))
        psf_image = SHEImage(np.random.randn(100).reshape(10,10))
        detections_table = initialise_detections_table()
        
        stack = SHEStack([data_image], [psf_image], [detections_table])
        
        