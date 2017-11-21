""" @file calibration_parameters_product.py

    Created 13 Oct 2017

    Functions to create and output a calibration parameters data product.
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
        Adds some extra functionality to the DpdCalibrationParameters product
    """
    
    # binding_class = she_dpd.DpdCalibrationParametersProduct # @FIXME
    binding_class = DpdSheCalibrationParametersProduct

    # Add the data file name methods
    
    binding_class.set_BFD_filename = __set_BFD_filename
    binding_class.get_BFD_filename = __get_BFD_filename
    
    binding_class.set_KSB_filename = __set_KSB_filename
    binding_class.get_KSB_filename = __get_KSB_filename
    
    binding_class.set_LensMC_filename = __set_LensMC_filename
    binding_class.get_LensMC_filename = __get_LensMC_filename
    
    binding_class.set_MomentsML_filename = __set_MomentsML_filename
    binding_class.get_MomentsML_filename = __get_MomentsML_filename
    
    binding_class.set_REGAUSS_filename = __set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = __get_REGAUSS_filename
    
    binding_class.get_all_filenames = __get_all_filenames
    
    binding_class.get_method_filename = __get_method_filename
    
    binding_class.has_files = True

def __set_BFD_filename(self, filename):
    self.Data.BFDCalibrationParameters.DataContainer.FileName = filename

def __get_BFD_filename(self):
    return self.Data.BFDCalibrationParameters.DataContainer.FileName

def __set_KSB_filename(self, filename):
    self.Data.KSBCalibrationParameters.DataContainer.FileName = filename

def __get_KSB_filename(self):
    return self.Data.KSBCalibrationParameters.DataContainer.FileName

def __set_LensMC_filename(self, filename):
    self.Data.LensMCCalibrationParameters.DataContainer.FileName = filename

def __get_LensMC_filename(self):
    return self.Data.LensMCCalibrationParameters.DataContainer.FileName

def __set_MomentsML_filename(self, filename):
    self.Data.MomentsMLCalibrationParameters.DataContainer.FileName = filename

def __get_MomentsML_filename(self):
    return self.Data.MomentsMLCalibrationParameters.DataContainer.FileName

def __set_REGAUSS_filename(self, filename):
    self.Data.REGAUSSCalibrationParameters.DataContainer.FileName = filename

def __get_REGAUSS_filename(self):
    return self.Data.REGAUSSCalibrationParameters.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = [self.get_BFD_filename(),
                     self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MomentsML_filename(),
                     self.get_REGAUSS_filename(),]
    
    return all_filenames

def __get_method_filename(self, method):
    
    if method=="BFD":
        return self.get_BFD_filename()
    elif method=="KSB":
        return self.get_KSB_filename()
    elif method=="LensMC":
        return self.get_LensMC_filename()
    elif method=="MomentsML":
        return self.get_MomentsML_filename()
    elif method=="REGAUSS":
        return self.get_REGAUSS_filename()
    elif method=="BFD":
        return None
    else:
        raise ValueError("Invalid method " + str(method) + ".")
    

class DpdSheCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class SheCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.BFDCalibrationParameters = None
        self.KSBCalibrationParameters = None
        self.LensMCCalibrationParameters = None
        self.MomentsMLCalibrationParameters = None
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
        
class SheMomentsMLCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheREGAUSSCalibrationParametersProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None

def create_dpd_she_calibration_parameters(BFD_filename = None,
                                          KSB_filename = None,
                                          LensMC_filename = None,
                                          MomentsML_filename = None,
                                          REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_calibration_parameters = she_dpd.DpdSheCalibrationParameters() # @FIXME
    dpd_calibration_parameters = DpdSheCalibrationParametersProduct()
    
    # dpd_calibration_parameters.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_calibration_parameters.Header = "SHE"
    
    dpd_calibration_parameters.Data = create_she_calibration_parameters(BFD_filename,
                                                                        KSB_filename,
                                                                        LensMC_filename,
                                                                        MomentsML_filename,
                                                                        REGAUSS_filename)
    
    return dpd_calibration_parameters

# Add a useful alias
create_calibration_parameters_product = create_dpd_she_calibration_parameters

def create_she_calibration_parameters(BFD_filename = None,
                                      KSB_filename = None,
                                      LensMC_filename = None,
                                      MomentsML_filename = None,
                                      REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # calibration_parameters = she_dpd.SheCalibrationParameters() # @FIXME
    calibration_parameters = SheCalibrationParametersProduct()
    
    calibration_parameters.BFDCalibrationParameters = create_she_BFD_calibration_parameters(BFD_filename)
    
    calibration_parameters.KSBCalibrationParameters = create_she_KSB_calibration_parameters(KSB_filename)
    
    calibration_parameters.LensMCCalibrationParameters = create_she_LensMC_calibration_parameters(LensMC_filename)
    
    calibration_parameters.MomentsMLCalibrationParameters = create_she_MomentsML_calibration_parameters(MomentsML_filename)
    
    calibration_parameters.REGAUSSCalibrationParameters = create_she_REGAUSS_calibration_parameters(REGAUSS_filename)
    
    return calibration_parameters

def create_she_BFD_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # BFD_calibration_parameters = she_dpd.SheBFDCalibrationParameters() # @FIXME
    BFD_calibration_parameters = SheBFDCalibrationParametersProduct()
    
    BFD_calibration_parameters.format = "UNDEFINED"
    BFD_calibration_parameters.version = "0.0"
    
    BFD_calibration_parameters.DataContainer = DataContainer()
    BFD_calibration_parameters.DataContainer.FileName = filename
    BFD_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return BFD_calibration_parameters

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

def create_she_MomentsML_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """
    
    # MomentsML_calibration_parameters = she_dpd.SheMomentsMLCalibrationParameters() # @FIXME
    MomentsML_calibration_parameters = SheMomentsMLCalibrationParametersProduct()
    
    MomentsML_calibration_parameters.format = "UNDEFINED"
    MomentsML_calibration_parameters.version = "0.0"
    
    MomentsML_calibration_parameters.DataContainer = DataContainer()
    MomentsML_calibration_parameters.DataContainer.FileName = filename
    MomentsML_calibration_parameters.DataContainer.filestatus = "PROPOSED"
    
    return MomentsML_calibration_parameters

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
