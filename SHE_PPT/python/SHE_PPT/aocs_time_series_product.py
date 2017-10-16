""" @file aocs_time_series_product.py

    Created 10 Oct 2017

    Functions to create and output an aocs_time_series data product.

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

# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

import pickle

def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """
    
    # binding_class = she_dpd.DpdSheAocsTimeSeriesProduct # @FIXME
    binding_class = DpdSheAocsTimeSeriesProduct
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = False
    
    return

def __get_all_filenames(self):
    
    all_filenames = []
    
    return all_filenames

class DpdSheAocsTimeSeriesProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheAocsTimeSeriesProduct: # @FIXME
    def __init__(self):
        pass

def create_dpd_she_aocs_time_series():
    """
        @TODO fill in docstring
    """
    
    # dpd_she_aocs_time_series = she_dpd.DpdSheAocsTimeSeriesProduct() # @FIXME
    dpd_she_aocs_time_series = DpdSheAocsTimeSeriesProduct()
    
    # dpd_she_aocs_time_series.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_aocs_time_series.Header = "SHE"
    
    dpd_she_aocs_time_series.Data = create_she_aocs_time_series()
    
    return dpd_she_aocs_time_series

# Add a useful alias
create_aocs_time_series_product = create_dpd_she_aocs_time_series

def create_she_aocs_time_series():
    """
        @TODO fill in docstring
    """
    
    # she_aocs_time_series = she_dpd.SheAocsTimeSeriesProduct() # @FIXME
    she_aocs_time_series = SheAocsTimeSeriesProduct()
    
    return she_aocs_time_series
