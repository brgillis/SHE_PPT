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
Author: user
"""

from __future__ import division, print_function
from future_builtins import *

import pytest
import SHE_PPT.she_image

import numpy as np


class Test_she_image():

    def test_init(self):
         
        size = 50
        array = np.random.randn(size**2).reshape((size, size))
        mask = np.zeros(size**2).reshape((size, size))
        a = SHE_PPT.she_image.SHEImage(array, mask)

        assert True



