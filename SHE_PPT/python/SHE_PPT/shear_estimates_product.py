""" @file shear_estimates_product.py

    Created 9 Oct 2017

    Functions to create and output a shear estimates data product.

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

from SHE_PPT.shear_estimates_table_format import tf as setf

def init():
    """
        Adds some extra functionality to the DpdShearEstimates product
    """
    
    # binding_class = she_dpd.DpdShearEstimatesProduct # @FIXME
    binding_class = DpdShearEstimatesProduct

    # Add the data file name methods
    
    binding_class.set_BFD_filename = __set_BFD_filename
    binding_class.get_BFD_filename = __get_BFD_filename
    
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

def __set_BFD_filename(self, filename):
    self.Data.BFDShearEstimates.DataContainer.FileName = filename

def __get_BFD_filename(self):
    return self.Data.BFDShearEstimates.DataContainer.FileName

def __set_KSB_filename(self, filename):
    self.Data.KSBShearEstimates.DataContainer.FileName = filename

def __get_KSB_filename(self):
    return self.Data.KSBShearEstimates.DataContainer.FileName

def __set_LensMC_filename(self, filename):
    self.Data.LensMCShearEstimates.DataContainer.FileName = filename

def __get_LensMC_filename(self):
    return self.Data.LensMCShearEstimates.DataContainer.FileName

def __set_MegaLUT_filename(self, filename):
    self.Data.MegaLUTShearEstimates.DataContainer.FileName = filename

def __get_MegaLUT_filename(self):
    return self.Data.MegaLUTShearEstimates.DataContainer.FileName

def __set_REGAUSS_filename(self, filename):
    self.Data.REGAUSSShearEstimates.DataContainer.FileName = filename

def __get_REGAUSS_filename(self):
    return self.Data.REGAUSSShearEstimates.DataContainer.FileName

def __get_all_filenames(self):
    
    all_filenames = [self.get_BFD_filename(),
                     self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MegaLUT_filename(),
                     self.get_REGAUSS_filename(),]
    
    return all_filenames

class DpdShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class ShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.BFDShearEstimates = None
        self.KSBShearEstimates = None
        self.LensMCShearEstimates = None
        self.MegaLUTShearEstimates = None
        self.REGAUSSShearEstimates = None
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None
        
class BFDShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class KSBShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class LensMCShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class MegaLUTShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class REGAUSSShearEstimatesProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None

def create_dpd_shear_estimates(BFD_filename = None,
                               KSB_filename = None,
                               LensMC_filename = None,
                               MegaLUT_filename = None,
                               REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_shear_estimates = she_dpd.DpdSheShearEstimates() # @FIXME
    dpd_shear_estimates = DpdShearEstimatesProduct()
    
    # dpd_shear_estimates.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_shear_estimates.Header = "SHE"
    
    dpd_shear_estimates.Data = create_shear_estimates(BFD_filename,
                                                       KSB_filename,
                                                       LensMC_filename,
                                                       MegaLUT_filename,
                                                       REGAUSS_filename)
    
    return dpd_shear_estimates

# Add a useful alias
create_shear_estimates_product = create_dpd_shear_estimates

def create_shear_estimates(BFD_filename = None,
                           KSB_filename = None,
                           LensMC_filename = None,
                           MegaLUT_filename = None,
                           REGAUSS_filename = None):
    """
        @TODO fill in docstring
    """
    
    # shear_estimates = she_dpd.SheShearEstimates() # @FIXME
    shear_estimates = ShearEstimatesProduct()
    
    shear_estimates.BFDShearEstimates = create_BFD_shear_estimates(BFD_filename)
    
    shear_estimates.KSBShearEstimates = create_KSB_shear_estimates(KSB_filename)
    
    shear_estimates.LensMCShearEstimates = create_LensMC_shear_estimates(LensMC_filename)
    
    shear_estimates.MegaLUTShearEstimates = create_MegaLUT_shear_estimates(MegaLUT_filename)
    
    shear_estimates.REGAUSSShearEstimates = create_REGAUSS_shear_estimates(REGAUSS_filename)
    
    return shear_estimates

def create_BFD_shear_estimates(filename):
    """
        @TODO fill in docstring
    """
    
    # BFD_shear_estimates = she_dpd.SheBFDShearEstimates() # @FIXME
    BFD_shear_estimates = BFDShearEstimatesProduct()
    
    BFD_shear_estimates.format = setf.m.table_format
    BFD_shear_estimates.version = setf.m.__version__
    
    BFD_shear_estimates.DataContainer = DataContainer()
    BFD_shear_estimates.DataContainer.FileName = filename
    BFD_shear_estimates.DataContainer.filestatus = "PROPOSED"
    
    return BFD_shear_estimates

def create_KSB_shear_estimates(filename):
    """
        @TODO fill in docstring
    """
    
    # KSB_shear_estimates = she_dpd.SheKSBShearEstimates() # @FIXME
    KSB_shear_estimates = KSBShearEstimatesProduct()
    
    KSB_shear_estimates.format = setf.m.table_format
    KSB_shear_estimates.version = setf.m.__version__
    
    KSB_shear_estimates.DataContainer = DataContainer()
    KSB_shear_estimates.DataContainer.FileName = filename
    KSB_shear_estimates.DataContainer.filestatus = "PROPOSED"
    
    return KSB_shear_estimates

def create_LensMC_shear_estimates(filename):
    """
        @TODO fill in docstring
    """
    
    # LensMC_shear_estimates = she_dpd.SheLensMCShearEstimates() # @FIXME
    LensMC_shear_estimates = LensMCShearEstimatesProduct()
    
    LensMC_shear_estimates.format = setf.m.table_format
    LensMC_shear_estimates.version = setf.m.__version__
    
    LensMC_shear_estimates.DataContainer = DataContainer()
    LensMC_shear_estimates.DataContainer.FileName = filename
    LensMC_shear_estimates.DataContainer.filestatus = "PROPOSED"
    
    return LensMC_shear_estimates

def create_MegaLUT_shear_estimates(filename):
    """
        @TODO fill in docstring
    """
    
    # MegaLUT_shear_estimates = she_dpd.SheMegaLUTShearEstimates() # @FIXME
    MegaLUT_shear_estimates = MegaLUTShearEstimatesProduct()
    
    MegaLUT_shear_estimates.format = setf.m.table_format
    MegaLUT_shear_estimates.version = setf.m.__version__
    
    MegaLUT_shear_estimates.DataContainer = DataContainer()
    MegaLUT_shear_estimates.DataContainer.FileName = filename
    MegaLUT_shear_estimates.DataContainer.filestatus = "PROPOSED"
    
    return MegaLUT_shear_estimates

def create_REGAUSS_shear_estimates(filename):
    """
        @TODO fill in docstring
    """
    
    # REGAUSS_shear_estimates = she_dpd.SheREGAUSSShearEstimates() # @FIXME
    REGAUSS_shear_estimates = REGAUSSShearEstimatesProduct()
    
    REGAUSS_shear_estimates.format = setf.m.table_format
    REGAUSS_shear_estimates.version = setf.m.__version__
    
    REGAUSS_shear_estimates.DataContainer = DataContainer()
    REGAUSS_shear_estimates.DataContainer.FileName = filename
    REGAUSS_shear_estimates.DataContainer.filestatus = "PROPOSED"
    
    return REGAUSS_shear_estimates
