""" @file she_ksb_calibration.py

    Created 24 Nov 2017

    Functions to create and output a ksb_calibration_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
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

__updated__ = "2021-06-09"


import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.ksbcalibration_stub import dpdSheKsbCalibration

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_ksb_calibration.xml"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdSheKsbCalibration

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    binding_class.set_data_filename = __set_filename
    binding_class.get_data_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_filename(self, filename):
    set_data_filename_of_product(self, filename, "KsbCalibrationFileList[0].DataStorage")


def __get_filename(self):
    return get_data_filename_from_product(self, "KsbCalibrationFileList[0].DataStorage")


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename()]

    return all_filenames


def create_dpd_she_ksb_calibration(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_ksb_calibration = read_xml_product(
        find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_ksb_calibration.Header = HeaderProvider.create_generic_header("DpdSheKsbCalibration")

    if filename:
        __set_filename(dpd_she_ksb_calibration, filename)

    return dpd_she_ksb_calibration


# Add a useful alias
create_ksb_calibration_data_product = create_dpd_she_ksb_calibration
