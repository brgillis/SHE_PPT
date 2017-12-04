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
from SHE_PPT.she_stack import SHEStack
import SHE_PPT.table_utility
import numpy as np


class Test_she_stack(object):
    
    @classmethod
    def setup_class(cls):
        
        # Filenames for testing the file io, will be deleted by teardown_class
        cls.sci_filepath_1 = "test_SHEStack_sci_SHEImage.fits"
        cls.det_filepath_1 = "test_SHEStack_det_Table.fits"
        cls.bpsf_filepath_1 = "test_SHEStack_bpsf_SHEImage.fits"
        cls.dpsf_filepath_1 = "test_SHEStack_dpsf_SHEImage.fits"
        cls.psfc_filepath_1 = "test_SHEStack_psfc_Table.fits"
        

    @classmethod
    def teardown_class(cls):
        
        # Delete all potentially created files:
        for testfilepath in [cls.sci_filepath_1, cls.det_filepath_1, cls.bpsf_filepath_1, cls.dpsf_filepath_1,
                             cls.psfc_filepath_1]:
            if os.path.exists(testfilepath):
                os.remove(testfilepath)


    def test_read(self):
        """We create the minimum required files, and read a SHEStack"""
        
        # Create what will be one exposure:
        sci_image = SHEImage(np.random.randn(100).reshape(10,10))
        bpsf_image = SHEImage(np.random.randn(100).reshape(10,10))
        dpsf_image = SHEImage(np.random.randn(100).reshape(10,10)) 
        det_table = initialise_detections_table()
        psf_table = initialise_psf_table()
        
        # Save those to files:
        sci_image.write_to_fits(self.sci_filepath_1)
        bpsf_image.write_to_fits(self.bpsf_filepath_1)
        dpsf_image.write_to_fits(self.dpsf_filepath_1)
        det_table.write(self.det_filepath_1)
        psf_table.write(self.psfc_filepath_1)
        
        
        # Read this, directly as a SHEStack
        
        filepaths_list = [
            [self.sci_filepath_1, self.det_filepath_1, self.bpsf_filepath_1, self.dpsf_filepath_1,
             self.psfc_filepath_1]
            ]
        
        mystack = SHEStack.read(filepaths_list, mask_ext='MASK') # Testing kwargs as well
        print(mystack.exposures[0].science_image)
        
        
        
        