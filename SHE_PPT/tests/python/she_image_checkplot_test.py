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
File: tests/python/she_image_checkplot_test.py

Created on: 10/19/17
Author: user
"""

from __future__ import division, print_function
from future_builtins import *

import py.test
import SHE_PPT.she_image_checkplot
import SHE_PPT.she_image
import numpy as np


import logging
logging.basicConfig(format='%(levelname)s: %(name)s(%(funcName)s): %(message)s', level=logging.DEBUG)


class Testshe_image_checkplot(object):
    """
    @class Testshe_image_checkplot
    @brief Unit Test class
    """
    @classmethod
    def setup_class(cls):
        cls.testfilepath = "test_checkplot.png"
       
    @classmethod
    def teardown_class(cls):
        pass
        #if os.path.exists(cls.testfilepath):
        #    os.remove(testfilepath)

    def test_checkplot(self):
        """
        
        """

        # Get some SHEImage
        
        array = np.random.randn(50, 30)
        array[4, 2] = 10
        mask = np.zeros(array.shape, dtype=bool)
        mask[10:15,:]=True
        
        img = SHE_PPT.she_image.SHEImage(array, mask=mask)
        
        
        
        checkplot = SHE_PPT.she_image_checkplot.Checkplot(img, scale=30)
        
        checkplot.draw()
        #checkplot.show()
        checkplot.save_to_file(self.testfilepath)
        
        
        
        
        
        
        
        

