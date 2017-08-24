""" @file test_table_formats.py

    Created 24 Aug 2017

    Unit tests relating to table formats.

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

import pytest

from SHE_PPT.details_table_format import tf as datf
from SHE_PPT.detections_table_format import tf as detf
from SHE_PPT.shear_estimates_table_format import tf as setf

from table_utility import (get_comments,
                           get_dtypes,
                           get_fits_dtypes,
                           is_in_format,
                           add_row,
                           output_tables,
                           output_table_as_fits,
                          )
class TestTableFormats:
    """


    """
    
    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats = [datf,detf,setf]
        
    @classmethod
    def teardown_class(cls):
        del cls.formats


    def testGetComments(self):
        # Check if we get the correct comments list for detections tables
        
        desired_comments = [None,"pixels","pixels","pixels","pixels"]
        
        assert get_comments(detf) == desired_comments
