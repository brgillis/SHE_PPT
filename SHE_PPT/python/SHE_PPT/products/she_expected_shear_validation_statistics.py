""" @file she_expected_shear_validation_statistics.py

    Created 17 Nov 2017

    Functions to create and output a she_expected_shear_validation_statistics data product.

    Origin: OU-SHE -  Output from Calibration pipeline and input to Analysis pipeline;
    must be persistent in archive.
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

__updated__ = "2020-06-25"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import pickle
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdSheExpectedShearValidationStatistics # @FIXME
    binding_class = DpdSheExpectedShearValidationStatistics

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename)


def __get_data_filename(self):
    return get_data_filename_from_product(self)


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


class DpdSheExpectedShearValidationStatistics:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheShearValidationStats:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_expected_shear_validation_statistics(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_expected_shear_validation_statistics =
    # she_dpd.DpdSheExpectedShearValidationStatistics() # FIXME
    dpd_she_expected_shear_validation_statistics = DpdSheExpectedShearValidationStatistics()

    # dpd_she_expected_shear_validation_statistics.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    dpd_she_expected_shear_validation_statistics.Header = "SHE"

    dpd_she_expected_shear_validation_statistics.Data = create_she_expected_shear_validation_statistics(
        filename)

    return dpd_she_expected_shear_validation_statistics


# Add a useful alias
create_expected_shear_validation_statistics_product = create_dpd_she_expected_shear_validation_statistics


def create_she_expected_shear_validation_statistics(filename=None):
    """
        @TODO fill in docstring
    """

    # she_expected_shear_validation_statistics = she_dpd.SheShearValidationStats() #
    # @FIXME
    she_expected_shear_validation_statistics = SheShearValidationStats()

    she_expected_shear_validation_statistics.format = "UNDEFINED"
    she_expected_shear_validation_statistics.version = "0.0"

    she_expected_shear_validation_statistics.DataContainer = DataContainer()
    she_expected_shear_validation_statistics.DataContainer.FileName = filename
    she_expected_shear_validation_statistics.DataContainer.filestatus = "PROPOSED"

    return she_expected_shear_validation_statistics
