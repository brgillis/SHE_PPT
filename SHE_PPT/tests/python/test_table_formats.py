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
import numpy as np

from SHE_PPT.details_table_format import tf as datf, initialise_details_table
from SHE_PPT.detections_table_format import tf as detf, initialise_detections_table
from SHE_PPT.shear_estimates_table_format import tf as setf, initialise_shear_estimates_table

from SHE_PPT.table_utility import (get_comments,
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
        cls.initializers = [initialise_details_table,
                            initialise_detections_table,
                            initialise_shear_estimates_table]
        
    @classmethod
    def teardown_class(cls):
        del cls.formats, cls.initializers


    def test_get_comments(self):
        # Check if we get the correct comments list for detections tables
        
        desired_comments = [None,"pixels","pixels","pixels","pixels"]
        
        assert get_comments(detf) == desired_comments
        
    def test_get_dtypes(self):
        # Check if we get the correct dtypes list for detections tables
        
        desired_dtypes = ["i8","f4","f4","f4","f4"]
        
        assert get_dtypes(detf) == desired_dtypes
        
    def test_get_fits_dtypes(self):
        # Check if we get the correct fits dtypes list for detections tables
        
        desired_fits_dtypes = ["K","E","E","E","E"]
        
        assert get_fits_dtypes(detf) == desired_fits_dtypes
        
    def test_is_in_format(self):
        # Test each format is detected correctly
        
        empty_tables = []
        
        for init in self.initializers:
            empty_tables.append(init())

        assert len(self.initializers) == len(self.table_formats) == 3
            
        for i in range(len(self.initializers)):
            for j in range((len(self.table_formats))):
                assert is_in_format(empty_tables[i],self.table_formats[j]) == (i==j)
