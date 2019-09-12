""" @file psf_calibration_params_product.py

    Created 10 Oct 2017

    Functions to create and output an psf_calibration_params data product.

    Origin: OU-SHE - Output from Calibration pipeline and input to Analysis pipeline;
    must be persistent in archive.

    The format here isn't finalised yet, but hopefully the needed information can all be stored in the FITS files.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2019-08-15"

# import HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import EuclidDmBindings.she.she_stub as she_dpd # FIXME

import pickle
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdShePSFCalibrationParams product
    """

    # binding_class = she_dpd.DpdShePSFCalibrationParamsProduct # @FIXME
    binding_class = DpdShePSFCalibrationParamsProduct

    # Add the data file name methods

    binding_class.set_zernike_mode_filename = __set_zernike_mode_filename
    binding_class.get_zernike_mode_filename = __get_zernike_mode_filename

    binding_class.set_surface_error_filename = __set_surface_error_filename
    binding_class.get_surface_error_filename = __get_surface_error_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True

    return


def __set_zernike_mode_filename(self, filename):
    set_data_filename_of_product(self, filename, "ZernikeMode")


def __get_zernike_mode_filename(self):
    return get_data_filename_from_product(self, "ZernikeMode")


def __set_surface_error_filename(self, filename):
    set_data_filename_of_product(self, filename, "SurfaceError")


def __get_surface_error_filename(self):
    return get_data_filename_from_product(self, "SurfaceError")


def __get_all_filenames(self):

    all_filenames = [self.get_zernike_mode_filename(),
                     self.get_surface_error_filename(), ]

    return all_filenames


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


class DpdShePSFCalibrationParamsProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class ShePSFCalibrationParamsProduct:  # @FIXME

    def __init__(self):
        self.TimeStamp = None
        self.TelescopeModel = None
        self.ZernikeMode = None
        self.SurfaceError = None
        self.DetectorModel = None
        self.Diagnostics = None


class SheTelescopeModelProduct:  # @FIXME

    def __init__(self):
        pass  # @TODO - Fill in format


class SheZernikeModeProduct:  # @FIXME

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
        pass  # @TODO - Fill in format


class SheDiagnosticsProduct:

    def __init__(self):
        pass  # @TODO - Fill in format


def create_dpd_she_psf_calibration_params(timestamp=None,
                                          zernike_mode_filename=None,
                                          surface_error_filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_psf_calibration_params =
    # she_dpd.DpdShePSFCalibrationParamsProduct() # @FIXME
    dpd_she_psf_calibration_params = DpdShePSFCalibrationParamsProduct()

    # dpd_she_psf_calibration_params.Header =
    # HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_psf_calibration_params.Header = "SHE"

    dpd_she_psf_calibration_params.Data = create_she_psf_calibration_params(timestamp,
                                                                            zernike_mode_filename,
                                                                            surface_error_filename)

    return dpd_she_psf_calibration_params


# Add a useful alias
create_psf_calibration_params_product = create_dpd_she_psf_calibration_params


def create_she_psf_calibration_params(timestamp=None,
                                      zernike_mode_filename=None,
                                      surface_error_filename=None):
    """
        @TODO fill in docstring
    """

    # she_psf_calibration_params = she_dpd.ShePSFCalibrationParamsProduct() #
    # @FIXME
    she_psf_calibration_params = ShePSFCalibrationParamsProduct()

    she_psf_calibration_params.TimeStamp = timestamp
    she_psf_calibration_params.TelescopeModel = create_she_telescope_model()
    she_psf_calibration_params.ZernikeMode = create_she_zernike_mode(
        zernike_mode_filename)
    she_psf_calibration_params.SurfaceError = create_she_surface_error(
        surface_error_filename)
    she_psf_calibration_params.DetectorModel = create_she_detector_model()
    she_psf_calibration_params.Diagnostics = create_she_diagnostics()

    return she_psf_calibration_params


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

    she_zernike_mode.format = "Undefined"  # @FIXME
    she_zernike_mode.version = "0.0"  # @FIXME

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

    she_surface_error.format = "Undefined"  # @FIXME
    she_surface_error.version = "0.0"  # @FIXME

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
