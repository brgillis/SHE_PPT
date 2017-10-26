""" @file mosaic_product.py

    Created 26 Oct 2017

    Functions to create and output a mosaic data product.

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
        Adds some extra functionality to the DpdMerMosaic product
    """
    
    # binding_class = she_dpd.DpdMerMosaicProduct # @FIXME
    binding_class = DpdMerMosaicProduct
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = False
    
    return

def __get_all_filenames(self):
    
    all_filenames = []
    
    return all_filenames

class DpdMerMosaicProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class MerMosaicProduct: # @FIXME
    def __init__(self):
        pass

def create_dpd_mer_mosaic():
    """
        @TODO fill in docstring
    """
    
    # dpd_mer_mosaic = she_dpd.DpdMerMosaicProduct() # @FIXME
    dpd_mer_mosaic = DpdMerMosaicProduct()
    
    # dpd_mer_mosaic.Header = HeaderProvider.createGenericHeader("MER") # FIXME
    dpd_mer_mosaic.Header = "MER"
    
    dpd_mer_mosaic.Data = create_mer_mosaic()
    
    return dpd_mer_mosaic

# Add a useful alias
create_mosaic_product = create_dpd_mer_mosaic

def create_mer_mosaic():
    """
        @TODO fill in docstring
    """
    
    # mer_mosaic = she_dpd.MerMosaicProduct() # @FIXME
    mer_mosaic = MerMosaicProduct()
    
    return mer_mosaic
