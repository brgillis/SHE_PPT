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

import os

import py.test

from SHE_PPT.table_formats.detections import initialise_detections_table
from SHE_PPT.table_formats.psf import initialise_psf_table
from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_image_stack import SHEImageStack
import SHE_PPT.table_utility
import numpy as np


class Test_she_stack(object):
    
    @classmethod
    def setup_class(cls):
        
        # Filenames for testing the file io, will be deleted by teardown_class
        cls.sci_filepath_1 = "test_SHEImageStack_sci_SHEImage.fits"
        cls.det_filepath_1 = "test_SHEImageStack_det_Table.fits"
        cls.bpsf_filepath_1 = "test_SHEImageStack_bpsf_SHEImage.fits"
        cls.dpsf_filepath_1 = "test_SHEImageStack_dpsf_SHEImage.fits"
        cls.psfc_filepath_1 = "test_SHEImageStack_psfc_Table.fits"
        

    @classmethod
    def teardown_class(cls):
        
        # Delete all potentially created files:
        for testfilepath in [cls.sci_filepath_1, cls.det_filepath_1, cls.bpsf_filepath_1, cls.dpsf_filepath_1,
                             cls.psfc_filepath_1]:
            if os.path.exists(testfilepath):
                os.remove(testfilepath)


    def test_read(self):
        """We create the minimum required files, and read a SHEImageStack"""
        
        # Create what will be one exposure:
        sci_image_1 = SHEImage(np.random.randn(100).reshape(10,10))
        sci_image_2 = SHEImage(np.random.randn(100).reshape(10,10))
        
        # Save those to files:
        sci_image_1.write_to_fits(self.sci_filepath_1)
        sci_image_2.write_to_fits(self.sci_filepath_2)
        
        
        # Read this, directly as a SHEImageStack
        
        filepaths_list = [
            [self.sci_filepath_1]
            [self.sci_filepath_2]
            ]
        
        mystack = SHEImageStack.read(filepaths_list, mask_ext='MASK') # Testing kwargs as well
        print(mystack.exposures[0].science_image)
        
        
        
        