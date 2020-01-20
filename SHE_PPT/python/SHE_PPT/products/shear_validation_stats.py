""" @file shear_validation_stats_product.py

    Created 17 Nov 2017

    Functions to create and output a shear_validation_stats data product.

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

__updated__ = "2019-08-15"


# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import pickle
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdSheShearValidationStatsProduct # @FIXME
    binding_class = DpdSheShearValidationStatsProduct

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


class DpdSheShearValidationStatsProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheShearValidationStatsProduct:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_shear_validation_stats(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_shear_validation_stats =
    # she_dpd.DpdSheShearValidationStatsProduct() # FIXME
    dpd_she_shear_validation_stats = DpdSheShearValidationStatsProduct()

    # dpd_she_shear_validation_stats.Header =
    # HeaderProvider.createGenericHeader("SHE") # FIXME
    dpd_she_shear_validation_stats.Header = "SHE"

    dpd_she_shear_validation_stats.Data = create_she_shear_validation_stats(
        filename)

    return dpd_she_shear_validation_stats


# Add a useful alias
create_shear_validation_stats_product = create_dpd_she_shear_validation_stats


def create_she_shear_validation_stats(filename=None):
    """
        @TODO fill in docstring
    """

    # she_shear_validation_stats = she_dpd.SheShearValidationStatsProduct() #
    # @FIXME
    she_shear_validation_stats = SheShearValidationStatsProduct()

    she_shear_validation_stats.format = "UNDEFINED"
    she_shear_validation_stats.version = "0.0"

    she_shear_validation_stats.DataContainer = DataContainer()
    she_shear_validation_stats.DataContainer.FileName = filename
    she_shear_validation_stats.DataContainer.filestatus = "PROPOSED"

    return she_shear_validation_stats
