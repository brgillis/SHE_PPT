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

from astropy.table import Table
import numpy as np
import os
import pytest

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
        
        cls.filename_base = "test_table"
        
        cls.filenames = [cls.filename_base+".ecsv", cls.filename_base+".fits"]
        
    @classmethod
    def teardown_class(cls):
        del cls.formats, cls.initializers
        
        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)


    def test_get_comments(self):
        # Check if we get the correct comments list for detections tables
        
        desired_comments = (None,"pixels","pixels","pixels","pixels")
        
        assert get_comments(detf) == desired_comments
        
    def test_get_dtypes(self):
        # Check if we get the correct dtypes list for detections tables
        
        desired_dtypes = ("i8","f4","f4","f4","f4")
        
        assert get_dtypes(detf) == desired_dtypes
        
    def test_get_fits_dtypes(self):
        # Check if we get the correct fits dtypes list for detections tables
        
        desired_fits_dtypes = ("K","E","E","E","E")
        
        assert get_fits_dtypes(detf) == desired_fits_dtypes
        
    def test_is_in_format(self):
        # Test each format is detected correctly
        
        empty_tables = []
        
        for init in self.initializers:
            empty_tables.append(init())

        assert len(self.initializers) == len(self.formats) == 3
            
        for i in range(len(self.initializers)):
            for j in range((len(self.formats))):
                assert is_in_format(empty_tables[i],self.formats[j]) == (i==j)
                
    def test_add_row(self):
        # Test that we can add a row through kwargs
        
        tab = initialise_detections_table()
        
        add_row(tab, **{detf.ID: 0, detf.gal_x: 0, detf.gal_y: 1, detf.psf_x: 10, detf.psf_y: 100})
        
        assert tab[detf.ID][0]==0
        assert tab[detf.gal_x][0]==0.
        assert tab[detf.gal_y][0]==1.
        assert tab[detf.psf_x][0]==10.
        assert tab[detf.psf_y][0]==100.
        
    def test_output_tables(self):
        
        # Clean up to make sure the test files don't already exist
        for filename in self.filenames:
            if os.path.exists(filename):
                os.remove(filename)
                
        
        tab = initialise_detections_table()
        
        add_row(tab, **{detf.ID: 0, detf.gal_x: 0, detf.gal_y: 1, detf.psf_x: 10, detf.psf_y: 100})
        
        # Try ascii output
        output_tables(tab,self.filename_base,"ascii")
        
        # Did it write properly?
        assert os.path.exists(self.filename_base+".ecsv")
        assert not os.path.exists(self.filename_base+".fits")
        
        # Can we read it?
        new_tab = Table.read(self.filename_base+".ecsv", format="ascii.ecsv")
        assert is_in_format(new_tab,detf)
        assert new_tab==tab
        
        # Cleanup
        os.remove(self.filename_base+".ecsv")
        
        # Try fits output
        output_tables(tab,self.filename_base,"fits")
        
        # Did it write properly?
        assert not os.path.exists(self.filename_base+".ecsv")
        assert os.path.exists(self.filename_base+".fits")
        
        # Can we read it?
        new_tab = Table.read(self.filename_base+".fits", format="fits")
        
        # Check that the column names are correct
        if new_tab.colnames != detf.all:
            assert False
        
        # Check the data types are correct
        desired_dtypes = get_dtypes(detf)
        for i in range(len(new_tab.colnames)):
            if new_tab.dtype[i] != np.dtype(desired_dtypes[i]):
                print(str(new_tab.dtype[i]))
                print(np.dtype(desired_dtypes[i]))
                assert False
            
        # Check the metadata is correct
        if new_tab.meta.keys() != detf.m.all:
            assert False
        
        # Check the version is correct
        if new_tab.meta[detf.m.version] != detf.__version__:
            assert False
        
        assert is_in_format(new_tab,detf)
        assert new_tab==tab
        
        # Cleanup
        os.remove(self.filename_base+".fits")
        
        # Try both output
        output_tables(tab,self.filename_base,"both")
        
        # Did it write properly?
        assert os.path.exists(self.filename_base+".ecsv")
        assert os.path.exists(self.filename_base+".fits")
        
        # Cleanup
        for filename in self.filenames:
            if os.path.exists(filename):
                os.remove(filename)