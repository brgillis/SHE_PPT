""" @file test_io.py

    Created 25 Aug 2017

    Unit tests relating to I/O functions.

    ---------------------------------------------------------------------

    Copyright (C) 2012-2020 Euclid Science Ground Segment      
       
    This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General    
    Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)    
    any later version.    
       
    This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied    
    warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more    
    details.    
       
    You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to    
    the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""

from astropy.table import Table
import numpy as np
import os
import pytest

from SHE_PPT.io import (get_allowed_filename,
                        write_listfile,
                        replace_in_file,
                        replace_multiple_in_file)

from time import sleep

class TestIO:
    """


    """
    
    @classmethod
    def setup_class(cls):
        pass
        
    @classmethod
    def teardown_class(cls):
        pass

    def test_get_allowed_filename(self):
        
        filename = get_allowed_filename( "TEST", "0", extension=".junk", release_date = "06.66")
        
        expect_filename_head = "EUC_SHE_CTE-TEST_0_"
        expect_filename_tail = ".0Z_06.66.junk"
        
        # Check the beginning and end are correct
        assert filename[0:len(expect_filename_head)]==expect_filename_head
        assert filename[-len(expect_filename_tail):]==expect_filename_tail
        
        # Check that if we wait a second, it will change
        sleep(1)
        new_filename = get_allowed_filename( "TEST", "0", extension=".junk", release_date = "06.66")
        assert new_filename > filename
        