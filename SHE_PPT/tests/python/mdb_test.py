""" @file mdb_test.py

    Created 15 Feb 2018

    Unit tests relating to MDB utility functions
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

from astropy.table import Table
import numpy as np
import os
import pytest

from SHE_PPT import mdb

class TestMDB:
    """


    """
    
    @classmethod
    def setup_class(cls):
        
        cls.test_key = "SpaceSegment.Instrument.VIS.VISDetectorPixelLongDimensionFormat"
        cls.filename = "AUX/SHE_PPT/EUC_MDB_MISSIONCONFIGURATION-SC3_2017-06-01T121200.00Z_01.01.xml"
        
        return
        
    @classmethod
    def teardown_class(cls):
        
        mdb.reset()
        
        return

    def test_get_mdb_details(self):
        # Test it works when initialised
        
        ex_value = 4136
        ex_value = 'This is the minimum number of pixels in the longest dimension of the VIS focal plane. Due to the injection line inserted in the long \n                direction of the CCD format, the active array is split in 2 equal active arrays, with 4 inactive pixels in the middle for injection line.'
        ex_source = 'Input by J.A. As required. Not validated, for test in the MDB. EUCL-EST-PS-7-001.'
        ex_release = '0.2'
        ex_expression = None
        ex_unit = 'pixel'
        
        mdb.init(self.filename)
        assert mdb.get_mdb_value(self.test_key)==ex_value
        assert mdb.get_mdb_description(self.test_key)==ex_description
        assert mdb.get_mdb_source(self.test_key)==ex_source
        assert mdb.get_mdb_release(self.test_key)==ex_release
        assert mdb.get_mdb_expression(self.test_key)==ex_expression
        assert mdb.get_mdb_unit(self.test_key)==ex_unit

    def test_get_mdb_exceptions(self):
        # Test it raises when not initialised
        mdb.reset()
        
        with pytest.raises(RuntimeError):
            mdb.get_mdb_value(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_description(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_source(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_release(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_expression(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_unit(self.test_key)
        
        
        