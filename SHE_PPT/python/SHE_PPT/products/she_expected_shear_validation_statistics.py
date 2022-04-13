""" @file she_expected_shear_validation_statistics.py

    Created 17 Nov 2017

    Functions to create and output a she_expected_shear_validation_statistics data product.

    Origin: OU-SHE -  Output from Calibration pipeline and input to Analysis pipeline;
    must be persistent in archive.
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

# Import dpdShePlaceHolderGeneral here since it's expected to be here
from ..product_utility import (ProductName, create_general_product_from_template, init_placeholder_general)

sample_file_name = 'SHE_PPT/sample_placeholder_general.xml'
product_type_name = "DpdSheExpectedShearValidationStatistics"


def init():
    """
        Adds some extra functionality to the product
    """

    init_placeholder_general(product_type_name = product_type_name,
                             init_function = create_dpd_she_expected_shear_validation_statistics)


def create_dpd_she_expected_shear_validation_statistics(filename = None):
    """ Initialize a product of this type
    """

    return create_general_product_from_template(template_filename = sample_file_name,
                                                product_type_name = product_type_name,
                                                general_product_type_name = ProductName.PLC_GENERAL.value,
                                                filename = filename, )
