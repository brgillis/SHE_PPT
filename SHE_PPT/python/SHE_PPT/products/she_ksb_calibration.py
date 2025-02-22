""" @file she_ksb_calibration.py

    Created 24 Nov 2017

    Functions to create and output a ksb_calibration_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
"""

__updated__ = "2021-08-16"

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


from ST_DataModelBindings.dpd.she.ksbcalibration_stub import dpdSheKsbCalibration
from ..product_utility import (create_product_from_template, get_all_filenames_just_data,
                               get_data_filename_from_product, init_binding_class, set_data_filename_of_product, )

sample_file_name = "SHE_PPT/sample_ksb_calibration.xml"
product_type_name = "DpdSheKsbCalibration"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdSheKsbCalibration

    if not init_binding_class(binding_class,
                              init_function=create_dpd_she_ksb_calibration):
        return

    # Add the data file name methods

    binding_class.set_filename = _set_filename
    binding_class.get_filename = _get_filename
    binding_class.set_data_filename = _set_filename
    binding_class.get_data_filename = _get_filename

    binding_class.get_all_filenames = get_all_filenames_just_data

    binding_class.has_files = True


def _set_filename(self, filename):
    set_data_filename_of_product(self, filename, "KsbCalibrationFileList[0].DataStorage")


def _get_filename(self):
    return get_data_filename_from_product(self, "KsbCalibrationFileList[0].DataStorage")


def create_dpd_she_ksb_calibration(filename=None,
                                   data_filename=None):
    """ Creates a product of this type.
    """

    return create_product_from_template(template_filename=sample_file_name,
                                        product_type_name=product_type_name,
                                        filename=filename,
                                        data_filename=data_filename)


# Add a useful alias
create_ksb_calibration_data_product = create_dpd_she_ksb_calibration
