""" @file exposure_mosaic_product.py

    Created 26 Oct 2017

    Functions to create and output a exposure_mosaic data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/she_exposure_mosaic.html
    
    Origin: OU-SHE - Internal to Analysis and Calibration pipelines. This version is
    converted from MER's version, so we need a separate product for it.
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

from astropy.io import fits
import os
import pickle

from SHE_PPT.file_io import read_xml_product
from SHE_PPT.utility import find_extension
from SHE_PPT import detector as dtc
import SHE_PPT.magic_values as mv

import HeaderProvider.GenericHeaderProvider as HeaderProvider

# Convenience function to easily load the actual map

def load_exposure_mosaic(filename, dir=None, **kwargs):
    """Directly loads the exposure_mosaic image from the filename of the data product.
    
    Parameters
    ----------
    filename : str
        Filename of the exposure_mosaic data product. If `dir` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `dir` is
        supplied, `filename` should be only the local name of the file.
    dir : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    **kwargs
        Keyword arguments to pass to fits.open.
        
    Returns
    -------
    exposure_mosaic_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the exposure_mosaic image and its header.
        
    Raises
    ------
    IOError
        Will raise an IOError if either no such file as `filename` exists or
        if the filename of the exposure_mosaic data contained within the product does
        not exist.
    """
    
    init()
    
    if dir is None:
        dir = ""
    
    exposure_mosaic_product = read_xml_product(xml_file_name = os.path.join(dir,filename))
    
    data_filename = exposure_mosaic_product.get_data_filename()
    
    exposure_mosaic_hdulist = fits.open(data_filename,**kwargs)
    
    return exposure_mosaic_hdulist[0]

# Initialisation function, to add methods to an imported XML class

def init():
    """
        Adds some extra functionality to the DpdSheExposureMosaic product
    """
    
    # binding_class = she_dpd.DpdSheExposureMosaicProduct # @FIXME
    binding_class = DpdSheExposureMosaicProduct
    
    if not hasattr(binding_class, "initialised"):
        binding_class.initialised = True
    else:
        return

    # Add the data file name methods
    
    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename
    
    return

def __set_data_filename(self, filename):
    self.Data.DataStorage.DataContainer.FileName = filename

def __get_data_filename(self):
    return self.Data.DataStorage.DataContainer.FileName
        
class DataContainer:
    def __init__(self):
        self.FileName = None
        self.filestatus = None

class DpdSheExposureMosaicProduct:
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return True
        
class SheExposureMosaicProduct:
    def __init__(self):
        self.DataStorage = None
    
class SheDataStorageProduct:
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        

def create_dpd_she_exposure_mosaic(data_filename):
    """
        @TODO fill in docstring
    """
    
    dpd_she_exposure_mosaic = DpdSheExposureMosaicProduct()
    
    dpd_she_exposure_mosaic.Header = HeaderProvider.createGenericHeader("SHE")
    
    dpd_she_exposure_mosaic.Data = create_she_exposure_mosaic(data_filename = data_filename)
    
    return dpd_she_exposure_mosaic

# Add a useful alias
create_exposure_mosaic_product = create_dpd_she_exposure_mosaic

def create_she_exposure_mosaic(data_filename):
    """
        @TODO fill in docstring
    """
    
    she_exposure_mosaic = SheExposureMosaicProduct()
    
    she_exposure_mosaic.DataStorage = create_she_data_storage(data_filename)
    
    return she_exposure_mosaic

def create_she_data_storage(filename):
    
    # she_data_storage = she_dpd.SheDataStorage() # @FIXME
    she_data_storage = SheDataStorageProduct()
    
    she_data_storage.format = "Undefined" # @FIXME
    she_data_storage.version = "0.0" # @FIXME
    
    she_data_storage.DataContainer = DataContainer()
    she_data_storage.DataContainer.FileName = filename
    she_data_storage.DataContainer.filestatus = "PROPOSED"
    
    return she_data_storage
