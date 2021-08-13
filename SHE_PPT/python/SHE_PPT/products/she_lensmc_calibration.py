""" @file she_lensmc_calibration.py

    Created 24 Nov 2017

    Functions to create and output a lensmc_calibration_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
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
from ST_DataModelBindings.dpd.she.lensmccalibration_stub import dpdSheLensMcCalibration

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_lensmc_calibration.xml"


def init():
    """
        Initialisers for LensMC calibration
    """

    binding_class = dpdSheLensMcCalibration

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


class DpdSheLensMcCalibration:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheLensMcCalibration:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_lensmc_calibration(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_lensmc_calibration = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_lensmc_calibration.Header = HeaderProvider.create_generic_header("DpdSheLensMcCalibration")

    if filename:
        _set_filename(dpd_she_lensmc_calibration, filename)
    return dpd_she_lensmc_calibration


# Add a useful alias
create_lensmc_calibration_data_product = create_dpd_she_lensmc_calibration


def create_she_lensmc_calibration(filename=None):
    """
        @TODO fill in docstring
    """

    she_lensmc_calibration = SheLensMcCalibration()

    she_lensmc_calibration.format = "she.lensMcMeasurements"
    she_lensmc_calibration.version = "8.0"

    she_lensmc_calibration.DataContainer = DataContainer()
    she_lensmc_calibration.DataContainer.FileName = filename
    she_lensmc_calibration.DataContainer.filestatus = "PROPOSED"

    return she_lensmc_calibration
