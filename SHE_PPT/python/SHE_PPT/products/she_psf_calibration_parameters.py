""" @file she_psf_calibration_parameters.py

    Created 24 Nov 2017

    Functions to create and output a psf_calibration_parameters data product.

    Origin: OU-SHE - Needs to be implemented in data model. Input to Analysis pipeline;
    must be persistent in archive.
"""

__updated__ = "2021-08-13"

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


import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.psfcalibrationparameters_stub import dpdShePsfCalibrationParameters

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_psf_calibration_parameters.xml"


def init():
    """
        Initialisers for LensMC training
    """

    binding_class = dpdShePsfCalibrationParameters

    # Add the data file name methods

    binding_class.set_filename = _set_filename
    binding_class.get_filename = _get_filename
    binding_class.set_data_filename = _set_filename
    binding_class.get_data_filename = _get_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.has_files = False


def _set_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def _get_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def _get_all_filenames(self):

    all_filenames = [self.get_filename()]

    return all_filenames


class DpdShePsfCalibrationParameters:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class ShePsfCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_psf_calibration_parameters(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_psf_calibration_parameters = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_psf_calibration_parameters.Header = HeaderProvider.create_generic_header("DpdShePsfCalibrationParameters")

    if filename:
        _set_filename(dpd_she_psf_calibration_parameters, filename)
    return dpd_she_psf_calibration_parameters


# Add a useful alias
create_psf_calibration_parameters_data_product = create_dpd_she_psf_calibration_parameters


def create_she_psf_calibration_parameters(filename=None):
    """
        @TODO fill in docstring
    """

    she_psf_calibration_parameters = ShePsfCalibrationParameters()

    she_psf_calibration_parameters.format = "she.psfCalibrationParameters"
    she_psf_calibration_parameters.version = "8.0"

    she_psf_calibration_parameters.DataContainer = DataContainer()
    she_psf_calibration_parameters.DataContainer.FileName = filename
    she_psf_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return she_psf_calibration_parameters
