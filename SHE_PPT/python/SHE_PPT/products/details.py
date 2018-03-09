""" @file details_product.py

    Created 17 Nov 2017

    Functions to create and output a details data product.
    
    Origin: OU-SHE - Internal to calibration pipeline.
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


# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

import pickle

def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """
    
    # binding_class = she_dpd.DpdSheGalaxyPopulationProduct # @FIXME
    binding_class = DpdSheGalaxyPopulationProduct

    # Add the data file name methods
    
    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = False
    
    return

def __set_filename(self, filename):
    self.Data.DataContainer.FileName = filename

def __get_filename(self):
    return self.Data.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = []
    
    return all_filenames

class DpdSheGalaxyPopulationProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheGalaxyPopulationProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

def create_dpd_she_details(filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_details = she_dpd.DpdSheGalaxyPopulationProduct() # FIXME
    dpd_she_details = DpdSheGalaxyPopulationProduct()
    
    # dpd_she_details.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_details.Header = "SHE"
    
    dpd_she_details.Data = create_she_details(filename)
    
    return dpd_she_details

# Add a useful alias
create_details_product = create_dpd_she_details

def create_she_details(filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_details = she_dpd.SheGalaxyPopulationProduct() # @FIXME
    she_details = SheGalaxyPopulationProduct()
    
    she_details.format = "UNDEFINED"
    she_details.version = "0.0"
    
    she_details.DataContainer = DataContainer()
    she_details.DataContainer.FileName = filename
    she_details.DataContainer.filestatus = "PROPOSED"
    
    return she_details
