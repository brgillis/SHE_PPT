""" @file table_formats_test.py

    Created 24 Aug 2017

    Unit tests relating to table formats.
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment      
#        
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General    
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)    
# any later version.    
#        
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied    
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more    
# details.    
#        
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to    
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import os

from astropy.table import Column, Table
import pytest

from SHE_PPT import magic_values as mv
from SHE_PPT.table_formats.details import tf as datf, initialise_details_table
from SHE_PPT.table_formats.detections import tf as detf, initialise_detections_table
from SHE_PPT.table_formats.galaxy_population import tf as gptf, initialise_galaxy_population_table
from SHE_PPT.table_formats.p_of_e import tf as petf, initialise_p_of_e_table
from SHE_PPT.table_formats.psf import tf as pstf, initialise_psf_table
from SHE_PPT.table_formats.shear_estimates import tf as setf, initialise_shear_estimates_table, len_chain, num_chains
from SHE_PPT.table_formats.simulation_plan import tf as sptf, initialise_simulation_plan_table
from SHE_PPT.table_utility import (get_comments,
                                   get_dtypes,
                                   get_fits_dtypes,
                                   get_lengths,
                                   is_in_format,
                                   add_row,
                                  )
import numpy as np


class TestTableFormats:
    """


    """
    
    @classmethod
    def setup_class(cls):
        # Define a list of the table formats we'll be testing
        cls.formats = [datf,detf,setf,petf,pstf,gptf,sptf]
        cls.initializers = [initialise_details_table,
                            initialise_detections_table,
                            initialise_shear_estimates_table,
                            initialise_p_of_e_table,
                            initialise_psf_table,
                            initialise_galaxy_population_table,
                            initialise_simulation_plan_table]
        
        cls.filename_base = "test_table"
        
        cls.filenames = [cls.filename_base+".ecsv", cls.filename_base+".fits"]
        
    @classmethod
    def teardown_class(cls):
        del cls.formats, cls.initializers
        
        for filename in cls.filenames:
            if os.path.exists(filename):
                os.remove(filename)

    def test_extra_data(self):
        # Check that the keys are assigned correctly for all extra data (eg. comments)
        
        # Loop over all formats
        for tf in self.formats:
            
            # Check metadata comments
            assert list(tf.m.comments.keys()) == tf.m.all
            
            # Check column comments
            assert list(tf.comments.keys()) == tf.all
            
            # Check column dtypes
            assert list(tf.dtypes.keys()) == tf.all
            
            # Check column fits dtypes
            assert list(tf.fits_dtypes.keys()) == tf.all
            
            # Check column lengths
            assert list(tf.lengths.keys()) == tf.all

    def test_get_comments(self):
        # Check if we get the correct comments list for detections tables
        
        desired_comments = (None,None,"pixel","pixel",
                            "pixel","pixel","deg",
                            "pixel**2","pixel**2","pixel","pixel","deg",
                            "deg","deg","deg","deg","deg",
                            "deg**2","deg**2","deg","deg","deg",
                            "deg","deg","deg","deg","deg",
                            "deg**2","deg**2","deg","deg","deg",
                            "deg","deg","deg","deg","deg","deg",
                            "VIS","VIS","pixel",None)
        
        assert get_comments(detf) == desired_comments
        
    def test_get_dtypes(self):
        # Check if we get the correct dtypes list for detections tables
        
        desired_dtypes = (">i8",">i8",">f4",">f4",
                            ">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">f4",">f4",">f4",
                            ">f4",">f4",">f4",">i8")
        
        assert get_dtypes(detf) == desired_dtypes
        
    def test_get_fits_dtypes(self):
        # Check if we get the correct fits dtypes list for detections tables
        
        desired_fits_dtypes = ("K","K","E","E",
                                "E","E","E",
                                "E","E","E","E","E",
                                "E","E","E","E","E",
                                "E","E","E","E","E",
                                "E","E","E","E","E",
                                "E","E","E","E","E",
                                "E","E","E","E","E","E",
                                "E","E","E","K")
        
        assert get_fits_dtypes(detf) == desired_fits_dtypes
        
    def test_get_lengths(self):
        # Check if we get the correct lengths list for shear estimates tables
        
        l = len_chain*num_chains
        
        desired_lengths = (1,1,1,1,1,1,1,
                           1,1,1,1,1,1,1,
                           1,1,1,1,1,1,1,
                           1,1,1,1,1,1,1,
                           1,1,1,1,1,1,1,
                           1,1,
                           7,7,7,7,7,7,7,7, ## BFD columns
                           7,7,1,1,6,15,3,  ## BFD columns
                           l,l,l,l,l,l,l,l,l,l)
 

       
        assert get_lengths(setf) == desired_lengths
        
    def test_is_in_format(self):
        # Test each format is detected correctly
        
        empty_tables = []
        
        for init in self.initializers:
            empty_tables.append(init())

        assert len(self.initializers) == len(self.formats)
            
        for i in range(len(self.initializers)):
            
            # Try strict test
            for j in range((len(self.formats))):
                assert is_in_format(empty_tables[i],self.formats[j],strict=True) == (i==j)
                
            # Try non-strict version now
            empty_tables[i].add_column(Column(name='new_column',data=np.zeros((0,))))
            for j in range((len(self.formats))):
                assert is_in_format(empty_tables[i],self.formats[j],strict=False) == (i==j)
                
    def test_add_row(self):
        # Test that we can add a row through kwargs
        
        tab = initialise_detections_table()
        
        add_row(tab, **{detf.ID: 0, detf.gal_x_world: 0, detf.gal_y_world: 1})
        
        assert tab[detf.ID][0]==0
        assert tab[detf.gal_x_world][0]==0.
        assert tab[detf.gal_y_world][0]==1.
                
    def test_init(self):
        
        detector_x = 3
        detector_y = 2
        model_hash = -1235
        model_seed = 4422
        noise_seed = 11015
        
        extname_head = "CCDID 3-2."
        
        # Test initialization methods
        
        detections_table = initialise_detections_table(detector_x = detector_x,
                                                       detector_y = detector_y)
        
        assert(detections_table.meta[detf.m.extname] == extname_head + mv.detections_tag)
        
        details_table = initialise_details_table(detector_x = detector_x,
                                                 detector_y = detector_y)
        
        assert(details_table.meta[detf.m.extname] == extname_head + mv.details_tag)
        
        psf_table = initialise_psf_table(detector_x = detector_x,
                                         detector_y = detector_y)
        
        assert(psf_table.meta[pstf.m.extname] == extname_head + mv.psf_cat_tag)
        
        # Try to initialize the shear estimates table based on the detections table
        
        detections_table.meta[detf.m.model_hash] = model_hash
        detections_table.meta[detf.m.model_seed] = model_seed
        detections_table.meta[detf.m.noise_seed] = noise_seed
        
        shear_estimates_table = initialise_shear_estimates_table(detections_table)
        
        assert(shear_estimates_table.meta[setf.m.extname] == extname_head + mv.shear_estimates_tag)
        assert(shear_estimates_table.meta[setf.m.model_hash] == model_hash)
        assert(shear_estimates_table.meta[setf.m.model_seed] == model_seed)
        assert(shear_estimates_table.meta[setf.m.noise_seed] == noise_seed)
        
        assert(shear_estimates_table.meta[setf.m.num_chains] == num_chains)
        assert(shear_estimates_table.meta[setf.m.len_chain] == len_chain)
        
