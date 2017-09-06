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
"""

from __future__ import division, print_function
from future_builtins import *

import py.test

import numpy as np
from SHE_PPT.she_stack import SHEStack
from SHE_PPT.she_image import SHEImage
from SHE_PPT.detections_table_format import initialise_detections_table
import SHE_PPT.table_utility


class Test_she_stack(object):
    
    @classmethod
    def setup_class(cls):
        
        # Filenames for testing the file io, will be deleted by teardown_class
        cls.sci_filepath_1 = "test_SHEStack_sci_SHEImage.fits"
        cls.det_filepath_1 = "test_SHEStack_det_Table.fits"
        cls.psf_filepath_1 = "test_SHEStack_psf_SHEImage.fits"
        

    @classmethod
    def teardown_class(cls):
        
        # Delete all potentially created files:
        for testfilepath in [cls.sci_filepath_1, cls.det_filepath_1, cls.psf_filepath_1]:
            if os.path.exists(testfilepath):
                os.remove(testfilepath)


    def test_read(self):
        """We create the minimum required files, and read a SHEStack"""
        
        # Create what will be one exposure:
        sci_image = SHEImage(np.random.randn(100).reshape(10,10))
        psf_image = SHEImage(np.random.randn(100).reshape(10,10))
        det_table = initialise_detections_table()
        
        # Save those to files:
        sci_image.write_to_fits(cls.sci_filepath_1)
        psf_image.write_to_fits(cls.psf_filepath_1)
        det_table.write(cls.det_filepath_1)
        
        
        # Read this, directly as a SHEStack
        
        filepaths_list = [
            [cls.sci_filepath_1, cls.det_filepath_1, cls.psf_filepath_1]
            ]
        
        mystack = SHEStack.read(filepaths_list)
        
        
        