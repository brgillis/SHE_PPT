""" @file calibrated_frame_product.py

    Created 17 Nov 2017

    Functions to create and output a calibrated_frame data product.
    
    Origin: OU-VIS
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
    
    # binding_class = she_dpd.DpdSheCalibratedFrameProduct # @FIXME
    binding_class = DpdSheCalibratedFrameProduct

    # Add the data file name methods
    
    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    
    binding_class.set_bkg_filename = __set_filename
    binding_class.get_bkg_filename = __get_filename
    
    return

def __set_filename(self, filename):
    self.Data.DataContainer.FileName = filename

def __get_filename(self):
    return self.Data.DataContainer.FileName

def __set_bkg_filename(self, filename):
    self.Data.BkgDataContainer.FileName = filename

def __get_bkg_filename(self):
    return self.Data.BkgDataContainer.FileName

class DpdSheCalibratedFrameProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheCalibratedFrameProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

def create_dpd_she_calibrated_frame(filename = None,
                                    bkg_filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_calibrated_frame = she_dpd.DpdSheCalibratedFrameProduct() # FIXME
    dpd_she_calibrated_frame = DpdSheCalibratedFrameProduct()
    
    # dpd_she_calibrated_frame.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_calibrated_frame.Header = "SHE"
    
    dpd_she_calibrated_frame.Data = create_she_calibrated_frame(filename)
    
    return dpd_she_calibrated_frame

# Add a useful alias
create_calibrated_frame_product = create_dpd_she_calibrated_frame

def create_she_calibrated_frame(filename = None,
                                bkg_filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_calibrated_frame = she_dpd.SheCalibratedFrameProduct() # @FIXME
    she_calibrated_frame = SheCalibratedFrameProduct()
    
    she_calibrated_frame.format = "UNDEFINED"
    she_calibrated_frame.version = "0.0"
    
    she_calibrated_frame.DataContainer = DataContainer()
    she_calibrated_frame.DataContainer.FileName = filename
    she_calibrated_frame.DataContainer.filestatus = "PROPOSED"
    
    she_calibrated_frame.BkgDataContainer = DataContainer()
    she_calibrated_frame.BkgDataContainer.FileName = bkg_filename
    she_calibrated_frame.BkgDataContainer.filestatus = "PROPOSED"
    
    return she_calibrated_frame
