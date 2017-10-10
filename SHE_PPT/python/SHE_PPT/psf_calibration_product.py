""" @file psf_calibration_product.py

    Created 10 Oct 2017

    Functions to create and output an psf_calibration data product.

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

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

import pickle

def init():
    """
        Adds some extra functionality to the DpdShePSFCalibration product
    """
    
    # binding_class = she_dpd.DpdShePSFCalibrationProduct # @FIXME
    binding_class = DpdShePSFCalibrationProduct

    # Add the data file name methods
    
    binding_class.set_zernike_mode_filename = __set_zernike_mode_filename
    binding_class.get_zernike_mode_filename = __get_zernike_mode_filename
    
    binding_class.set_surface_error_filename = __set_surface_error_filename
    binding_class.get_surface_error_filename = __get_surface_error_filename
    
    return

def __set_zernike_mode_filename(self, filename):
    self.Data.ZernikeMode.DataContainer.FileName = filename

def __get_zernike_mode_filename(self):
    return self.Data.ZernikeMode.DataContainer.FileName

def __set_surface_error_filename(self, filename):
    self.Data.SurfaceError.DataContainer.FileName = filename

def __get_surface_error_filename(self):
    return self.Data.SurfaceError.DataContainer.FileName
        
class DataContainer: # @FIXME
    def __init__(self):
        self.FileName = None
        self.filestatus = None

class DpdShePSFCalibrationProduct: # @FIXME
    def __init__(self):
        self.Header = None
        self.Data = None
    def validateBinding(self):
        return False
        
class ShePSFCalibrationProduct: # @FIXME
    def __init__(self):
        self.TimeStamp = None
        self.TelescopeModel = None
        self.ZernikeMode = None
        self.SurfaceError = None
        self.DetectorModel = None
        self.Diagnostics = None
        
class SheTelescopeModelProduct: # @FIXME
    def __init__(self):
        pass # @TODO - Fill in format
    
class SheZernikeModeProduct: # @FIXME
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheSurfaceErrorProduct:
    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None
        
class SheDetectorModelProduct:
    def __init__(self):
        pass # @TODO - Fill in format
    
class SheDiagnosticsProduct:
    def __init__(self):
        pass # @TODO - Fill in format

def create_dpd_she_psf_calibration(timestamp = None,
                                   zernike_mode_filename = None,
                                   surface_error_filename = None):
    """
        @TODO fill in docstring
    """
    
    # dpd_she_psf_calibration = she_dpd.DpdShePSFCalibrationProduct() # @FIXME
    dpd_she_psf_calibration = DpdShePSFCalibrationProduct()
    
    # dpd_she_psf_calibration.Header = HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_psf_calibration.Header = "SHE"
    
    dpd_she_psf_calibration.Data = create_she_psf_calibration(timestamp,
                                                              zernike_mode_filename,
                                                              surface_error_filename)
    
    return dpd_she_psf_calibration

def create_she_psf_calibration(timestamp = None,
                               zernike_mode_filename = None,
                               surface_error_filename = None):
    """
        @TODO fill in docstring
    """
    
    # she_psf_calibration = she_dpd.ShePSFCalibrationProduct() # @FIXME
    she_psf_calibration = ShePSFCalibrationProduct()
    
    she_psf_calibration.TimeStamp = timestamp
    she_psf_calibration.SheTelescopeModel = create_she_telescope_model()
    she_psf_calibration.SheZernikeMode = create_she_zernike_mode(zernike_mode_filename)
    she_psf_calibration.SheSurfaceError = create_she_surface_error(surface_error_filename)
    she_psf_calibration.SheDetectorModel = create_she_detector_model()
    she_psf_calibration.SheDiagnostics = create_she_diagnostics()
    
    return she_psf_calibration

def create_she_telescope_model():
    """
        @TODO fill in docstring
    """
    
    # she_telescope_model = she_dpd.SheTelescopeModelProduct() # @FIXME
    she_telescope_model = SheTelescopeModelProduct()
    
    return she_telescope_model

def create_she_zernike_mode(filename):
    """
        @TODO fill in docstring
    """
    
    # she_zernike_mode = she_dpd.SheZernikeModeProduct() # @FIXME
    she_zernike_mode = SheZernikeModeProduct()
    
    she_zernike_mode.format = "Undefined" # @FIXME
    she_zernike_mode.version = "0.0" # @FIXME
    
    she_zernike_mode.DataContainer = DataContainer()
    she_zernike_mode.DataContainer.FileName = filename
    she_zernike_mode.DataContainer.filestatus = "PROPOSED"
    
    return she_zernike_mode

def create_she_surface_error(filename):
    """
        @TODO fill in docstring
    """
    
    # she_surface_error = she_dpd.SheSurfaceErrorProduct() # @FIXME
    she_surface_error = SheSurfaceErrorProduct()
    
    she_surface_error.format = "Undefined" # @FIXME
    she_surface_error.version = "0.0" # @FIXME
    
    she_surface_error.DataContainer = DataContainer()
    she_surface_error.DataContainer.FileName = filename
    she_surface_error.DataContainer.filestatus = "PROPOSED"
    
    return she_surface_error
    
def create_she_detector_model():
    """
        @TODO fill in docstring
    """
    
    # she_detector_model = she_dpd.SheDetectorModelProduct() # @FIXME
    she_detector_model = SheDetectorModelProduct()
    
    return she_detector_model
    
def create_she_diagnostics():
    """
        @TODO fill in docstring
    """
    
    # she_diagnostics = she_dpd.SheDiagnosticsProduct() # @FIXME
    she_diagnostics = SheDiagnosticsProduct()
    
    return she_diagnostics
    
