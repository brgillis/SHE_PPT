""" @file detections_product.py

    Created 17 Nov 2017

    Functions to create and output a detections data product.
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
    
    # binding_class = she_dpd.DpdSheDetectionsProduct # @FIXME
    binding_class = DpdSheDetectionsProduct

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

class DpdSheDetectionsProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheDetectionsProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

def create_dpd_she_detections(filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_detections = she_dpd.DpdSheDetectionsProduct() # FIXME
    dpd_she_detections = DpdSheDetectionsProduct()
    
    # dpd_she_detections.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_detections.Header = "SHE"
    
    dpd_she_detections.Data = create_she_detections(filename)
    
    return dpd_she_detections

# Add a useful alias
create_detections_product = create_dpd_she_detections

def create_she_detections(filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_detections = she_dpd.SheDetectionsProduct() # @FIXME
    she_detections = SheDetectionsProduct()
    
    she_detections.format = "UNDEFINED"
    she_detections.version = "0.0"
    
    she_detections.DataContainer = DataContainer()
    she_detections.DataContainer.FileName = filename
    she_detections.DataContainer.filestatus = "PROPOSED"
    
    return she_detections
