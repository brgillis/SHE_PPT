""" @file bfd_training_data_product.py

    Created 24 Nov 2017

    Functions to create and output a bfd_training_data data product.
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
    
    # binding_class = she_dpd.DpdSheBFDTrainingDataProduct # @FIXME
    binding_class = DpdSheBFDTrainingDataProduct

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

class DpdSheBFDTrainingDataProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheBFDTrainingDataProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

def create_dpd_she_bfd_training_data(filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_bfd_training_data = she_dpd.DpdSheBFDTrainingDataProduct() # FIXME
    dpd_she_bfd_training_data = DpdSheBFDTrainingDataProduct()
    
    # dpd_she_bfd_training_data.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_bfd_training_data.Header = "SHE"
    
    dpd_she_bfd_training_data.Data = create_she_bfd_training_data(filename)
    
    return dpd_she_bfd_training_data

# Add a useful alias
create_bfd_training_data_product = create_dpd_she_bfd_training_data

def create_she_bfd_training_data(filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_bfd_training_data = she_dpd.SheBFDTrainingDataProduct() # @FIXME
    she_bfd_training_data = SheBFDTrainingDataProduct()
    
    she_bfd_training_data.format = "UNDEFINED"
    she_bfd_training_data.version = "0.0"
    
    she_bfd_training_data.DataContainer = DataContainer()
    she_bfd_training_data.DataContainer.FileName = filename
    she_bfd_training_data.DataContainer.filestatus = "PROPOSED"
    
    return she_bfd_training_data
