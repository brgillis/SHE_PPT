""" @file mosaic_product.py

    Created 26 Oct 2017

    Functions to create and output a mosaic data product, per details at
    http://euclid.esac.esa.int/dm/dpdd/latest/merdpd/dpcards/mer_mosaic.html

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
# import EuclidDmBindings.she.she_stub as mer_dpd # FIXME

from astropy.io import fits
import os
import pickle

from SHE_PPT.file_io import read_xml_product

# Convenience function to easily load the actual map

def load_mosaic_hdu(filename, listfile_filename=None, dir=None, **kwargs):
    """Directly loads the mosaic image from the filename of the data product.
    
    Parameters
    ----------
    filename : str
        Filename of the mosaic data product. If `dir` is None, `filename `must
        be either fully-qualified or relative to the workspace. If `dir` is
        supplied, `filename` should be only the local name of the file.
    listfile_filename : str
        Filename of the mosaic data product's associate listfile. If `dir` is
        None, `listfile_filename` must be either fully-qualified or relative to
        the workspace. If `dir` is supplied, `filename` should be only the
        local name of the file.
    dir : str
        Directory in which `filename` is contained. If not supplied, `filename`
        and `listfile_filename` (if supplied) will be assumed to be either
        fully-qualified or relative to the workspace.
    **kwargs
        Keyword arguments to pass to fits.open.
        
    Returns
    -------
    mosaic_hdu : astropy.fits.PrimaryHDU
        fits HDU containing the mosaic image and its header.
        
    Raises
    ------
    ValueError
        Will raise a ValueError if either no such file as `filename` exists or
        if the filename of the mosaic data contained within the product does
        not exist.
    """
    
    init()
    
    if dir is None:
        dir = ""
    
    mosaic_product = read_xml_product(xml_file_name = os.path.join(dir,filename),
                                      listfile_file_name = os.path.join(dir,listfile_filename))
    
    mosaic_hdu = fits.open(mosaic_product.get_data_filename(),**kwargs)[0]
    
    return mosaic_hdu

# Initialisation function, to add methods to an imported XML class

def init():
    """
        Adds some extra functionality to the DpdMerMosaic product
    """
    
    # binding_class = mer_dpd.DpdMerMosaicProduct # @FIXME
    binding_class = DpdMerMosaicProduct
    
    if not hasattr(binding_class, "initialised"):
        binding_class.initialised = True
    else:
        return

    # Add the data file name methods
    
    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename
    
    binding_class.set_rms_filename = __set_rms_filename
    binding_class.get_rms_filename = __get_rms_filename
    
    binding_class.set_flag_filename = __set_flag_filename
    binding_class.get_flag_filename = __get_flag_filename
    
    binding_class.set_psf_model_filename = __set_psf_model_filename
    binding_class.get_psf_model_filename = __get_psf_model_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = True
    
    return

def __set_data_filename(self, filename):
    self.Data.DataStorage.DataContainer.FileName = filename

def __get_data_filename(self):
    return self.Data.DataStorage.DataContainer.FileName

def __set_rms_filename(self, filename):
    self.Data.RmsStorage.DataContainer.FileName = filename

def __get_rms_filename(self):
    return self.Data.RmsStorage.DataContainer.FileName

def __set_flag_filename(self, filename):
    self.Data.FlagStorage.DataContainer.FileName = filename

def __get_flag_filename(self):
    return self.Data.FlagStorage.DataContainer.FileName

def __set_psf_model_filename(self, filename):
    self.Data.PsfModelStorage.DataContainer.FileName = filename

def __get_psf_model_filename(self):
    return self.Data.PsfModelStorage.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = [self.get_data_filename(),
                     self.get_rms_filename(),
                     self.get_flag_filename(),
                     self.get_psf_model_filename(),]
    
    return all_filenames
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

class DpdMerMosaicProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class MerMosaicProduct: # @FIXME
    def __init__(self):
        self.Instrument = None
        self.Filter = None
        self.WCS = None
        self.ZeroPoint = None
        self.FieldIdList = None
        self.ImgSpatialFootprint = None
        self.Masks = None
        self.DataStorage = None
        self.RmsStorage = None
        self.FlagStorage = None
        self.PsfModelStorage = None
        self.ProcessingSteps = None
        
class MerWcsProduct:
    def __init__(self):
        pass # @TODO - Fill in format
        
class MerImageSpatialFootprintProduct:
    def __init__(self):
        pass # @TODO - Fill in format
        
class MerProcessingStepsProduct:
    def __init__(self):
        pass # @TODO - Fill in format
    
class MerDataStorageProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
    
class MerRmsStorageProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
    
class MerFlagStorageProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
    
class MerPsfModelStorageProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        

def create_dpd_mer_mosaic(instrument_name,
                          filter,
                          wcs_params,
                          zeropoint,
                          data_filename,
                          field_id_list = None,
                          img_spatial_footprint_params = None,
                          masks = None,
                          rms_filename = None,
                          flag_filename = None,
                          psf_model_filename = None,
                          processing_steps_params = None
                          ):
    """
        @TODO fill in docstring
    """
    
    # dpd_mer_mosaic = mer_dpd.DpdMerMosaicProduct() # @FIXME
    dpd_mer_mosaic = DpdMerMosaicProduct()
    
    # dpd_mer_mosaic.Header = HeaderProvider.createGenericHeader("MER") # FIXME
    dpd_mer_mosaic.Header = "MER"
    
    dpd_mer_mosaic.Data = create_mer_mosaic(instrument_name = instrument_name,
                                          filter = filter,
                                          wcs_params = wcs_params,
                                          zeropoint = zeropoint,
                                          data_filename = data_filename,
                                          field_id_list = field_id_list,
                                          img_spatial_footprint_params = img_spatial_footprint_params,
                                          masks = masks,
                                          rms_filename = rms_filename,
                                          flag_filename = flag_filename,
                                          psf_model_filename = psf_model_filename,
                                          processing_steps_params = processing_steps_params
                                          )
    
    return dpd_mer_mosaic

# Add a useful alias
create_mosaic_product = create_dpd_mer_mosaic

def create_mer_mosaic(instrument_name,
                      filter,
                      wcs_params,
                      zeropoint,
                      data_filename,
                      field_id_list,
                      img_spatial_footprint_params,
                      masks,
                      rms_filename,
                      flag_filename,
                      psf_model_filename,
                      processing_steps_params
                      ):
    """
        @TODO fill in docstring
    """
    
    if field_id_list is None:
        field_id_list = []
    
    # mer_mosaic = mer_dpd.MerMosaicProduct() # @FIXME
    mer_mosaic = MerMosaicProduct()
    
    mer_mosaic.Instrument = instrument_name
    mer_mosaic.Filter = filter
    mer_mosaic.WCS = create_mer_wcs(wcs_params)
    mer_mosaic.ZeroPoint = zeropoint
    mer_mosaic.FieldIdList = field_id_list
    mer_mosaic.ImgSpatialFootprint = create_mer_image_spatial_footprint(img_spatial_footprint_params)
    mer_mosaic.Masks = masks
    mer_mosaic.DataStorage = create_mer_data_storage(data_filename)
    mer_mosaic.RmsStorage = create_mer_rms_storage(rms_filename)
    mer_mosaic.FlagStorage = create_mer_flag_storage(flag_filename)
    mer_mosaic.PsfModelStorage = create_mer_psf_model_storage(psf_model_filename)
    mer_mosaic.ProcessingSteps = create_mer_processing_steps(processing_steps_params)
    
    return mer_mosaic

def create_mer_wcs(wcs_params):
    """
        @TODO fill in docstring
    """
    
    # mer_wcs = mer_dpd.MerWcs() # @FIXME
    mer_wcs = MerWcsProduct()
    
    return mer_wcs

def create_mer_image_spatial_footprint(image_spatial_footprint_params):
    """
        @TODO fill in docstring
    """
    
    # mer_image_spatial_footprint = mer_dpd.MerImageSpatialFootprint() # @FIXME
    mer_image_spatial_footprint = MerImageSpatialFootprintProduct()
    
    return mer_image_spatial_footprint

def create_mer_processing_steps(processing_steps_params):
    """
        @TODO fill in docstring
    """
    
    # mer_processing_steps = mer_dpd.MerProcessingSteps() # @FIXME
    mer_processing_steps = MerProcessingStepsProduct()
    
    return mer_processing_steps

def create_mer_data_storage(filename):
    
    # mer_data_storage = mer_dpd.MerDataStorage() # @FIXME
    mer_data_storage = MerDataStorageProduct()
    
    mer_data_storage.format = "Undefined" # @FIXME
    mer_data_storage.version = "0.0" # @FIXME
    
    mer_data_storage.DataContainer = DataContainer()
    mer_data_storage.DataContainer.FileName = filename
    mer_data_storage.DataContainer.filestatus = "PROPOSED"
    
    return mer_data_storage

def create_mer_rms_storage(filename):
    
    # mer_rms_storage = mer_dpd.MerRmsStorage() # @FIXME
    mer_rms_storage = MerRmsStorageProduct()
    
    mer_rms_storage.format = "Undefined" # @FIXME
    mer_rms_storage.version = "0.0" # @FIXME
    
    mer_rms_storage.DataContainer = DataContainer()
    mer_rms_storage.DataContainer.FileName = filename
    mer_rms_storage.DataContainer.filestatus = "PROPOSED"
    
    return mer_rms_storage

def create_mer_flag_storage(filename):
    
    # mer_flag_storage = mer_dpd.MerFlagStorage() # @FIXME
    mer_flag_storage = MerFlagStorageProduct()
    
    mer_flag_storage.format = "Undefined" # @FIXME
    mer_flag_storage.version = "0.0" # @FIXME
    
    mer_flag_storage.DataContainer = DataContainer()
    mer_flag_storage.DataContainer.FileName = filename
    mer_flag_storage.DataContainer.filestatus = "PROPOSED"
    
    return mer_flag_storage

def create_mer_psf_model_storage(filename):
    
    # mer_psf_model_storage = mer_dpd.MerPsfModelStorage() # @FIXME
    mer_psf_model_storage = MerPsfModelStorageProduct()
    
    mer_psf_model_storage.format = "Undefined" # @FIXME
    mer_psf_model_storage.version = "0.0" # @FIXME
    
    mer_psf_model_storage.DataContainer = DataContainer()
    mer_psf_model_storage.DataContainer.FileName = filename
    mer_psf_model_storage.DataContainer.filestatus = "PROPOSED"
    
    return mer_psf_model_storage
