""" @file calibration_parameters_product.py

    Created 13 Oct 2017

    Functions to create and output a calibration parameters data product.

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
        Adds some extra functionality to the DpdCalibrationParameters product
    """
    
    # binding_class = she_dpd.DpdCalibrationParametersProduct # @FIXME
    binding_class = DpdCalibrationParametersProduct

    # Add the data file name methods
    
    binding_class.set_KSB_filename = __set_KSB_filename
    binding_class.get_KSB_filename = __get_KSB_filename
    
    binding_class.set_LensMC_filename = __set_LensMC_filename
    binding_class.get_LensMC_filename = __get_LensMC_filename
    
    binding_class.set_MegaLUT_filename = __set_MegaLUT_filename
    binding_class.get_MegaLUT_filename = __get_MegaLUT_filename
    
    binding_class.set_REGAUSS_filename = __set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = __get_REGAUSS_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.has_files = True

def __set_KSB_filename(self, filename):
    self.Data.KSBCalibrationParameters.DataContainer.FileName = filename

def __get_KSB_filename(self):
    return self.Data.KSBCalibrationParameters.DataContainer.FileName

def __set_LensMC_filename(self, filename):
    self.Data.LensMCCalibrationParameters.DataContainer.FileName = filename

def __get_LensMC_filename(self):
    return self.Data.LensMCCalibrationParameters.DataContainer.FileName

def __set_MegaLUT_filename(self, filename):
    self.Data.MegaLUTCalibrationParameters.DataContainer.FileName = filename

def __get_MegaLUT_filename(self):
    return self.Data.MegaLUTCalibrationParameters.DataContainer.FileName

def __set_REGAUSS_filename(self, filename):
    self.Data.REGAUSSCalibrationParameters.DataContainer.FileName = filename

def __get_REGAUSS_filename(self):
    return self.Data.REGAUSSCalibrationParameters.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = [self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MegaLUT_filename(),
                     self.get_REGAUSS_filename(),]
    
    return all_filenames

class DpdSheCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.KSBCalibrationParameters = None
        self.LensMCCalibrationParameters = None
        self.MegaLUTCalibrationParameters = None
        self.REGAUSSCalibrationParameters = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None
        
class SheBFDCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheKSBCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheLensMCCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheMegaLUTCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheREGAUSSCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None

def create_dpd_she_calibration_parameters(KSB_filename = None,
                               LensMC_filename = None,
                               MegaLUT_filename = None,
                               REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_calibration_parameters = she_dpd.DpdSheCalibrationParameters() # @FIXME
    dpd_calibration_parameters = DpdCalibrationParametersProduct()
    
    # dpd_calibration_parameters.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_calibration_parameters.Header = "SHE"
    
    dpd_calibration_parameters.Data = create_she_calibration_parameters(KSB_filename,
                                                       LensMC_filename,
                                                       MegaLUT_filename,
                                                       REGAUSS_filename)
    
    return dpd_calibration_parameters

# Add a useful alias
create_calibration_parameters_product = create_dpd_she_calibration_parameters

def create_she_calibration_parameters(KSB_filename = None,
                           LensMC_filename = None,
                           MegaLUT_filename = None,
                           REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # calibration_parameters = she_dpd.SheCalibrationParameters() # @FIXME
    calibration_parameters = SheCalibrationParametersProduct()
    
    calibration_parameters.KSBCalibrationParameters = create_KSB_calibration_parameters(KSB_filename)
    
    calibration_parameters.LensMCCalibrationParameters = create_LensMC_calibration_parameters(LensMC_filename)
    
    calibration_parameters.MegaLUTCalibrationParameters = create_MegaLUT_calibration_parameters(MegaLUT_filename)
    
    calibration_parameters.REGAUSSCalibrationParameters = create_REGAUSS_calibration_parameters(REGAUSS_filename)
    
    return calibration_parameters

def create_she_KSB_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # KSB_calibration_parameters = she_dpd.SheKSBCalibrationParameters() # @FIXME
    KSB_calibration_parameters = SheKSBCalibrationParametersProduct()
    
    KSB_calibration_parameters.format = "UNDEFINED"
    KSB_calibration_parameters.version = "0.0"
    
    KSB_calibration_parameters.DataContainer = DataContainer()
    KSB_calibration_parameters.DataContainer.FileName = filename
    KSB_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return KSB_calibration_parameters

def create_she_LensMC_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # LensMC_calibration_parameters = she_dpd.SheLensMCCalibrationParameters() # @FIXME
    LensMC_calibration_parameters = SheLensMCCalibrationParametersProduct()
    
    LensMC_calibration_parameters.format = "UNDEFINED"
    LensMC_calibration_parameters.version = "0.0"
    
    LensMC_calibration_parameters.DataContainer = DataContainer()
    LensMC_calibration_parameters.DataContainer.FileName = filename
    LensMC_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return LensMC_calibration_parameters

def create_she_MegaLUT_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # MegaLUT_calibration_parameters = she_dpd.SheMegaLUTCalibrationParameters() # @FIXME
    MegaLUT_calibration_parameters = SheMegaLUTCalibrationParametersProduct()
    
    MegaLUT_calibration_parameters.format = "UNDEFINED"
    MegaLUT_calibration_parameters.version = "0.0"
    
    MegaLUT_calibration_parameters.DataContainer = DataContainer()
    MegaLUT_calibration_parameters.DataContainer.FileName = filename
    MegaLUT_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return MegaLUT_calibration_parameters

def create_she_REGAUSS_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # REGAUSS_calibration_parameters = she_dpd.SheREGAUSSCalibrationParameters() # @FIXME
    REGAUSS_calibration_parameters = SheREGAUSSCalibrationParametersProduct()
    
    REGAUSS_calibration_parameters.format = "UNDEFINED"
    REGAUSS_calibration_parameters.version = "0.0"
    
    REGAUSS_calibration_parameters.DataContainer = DataContainer()
    REGAUSS_calibration_parameters.DataContainer.FileName = filename
    REGAUSS_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return REGAUSS_calibration_parameters
