""" @file she_expected_shear_validation_statistics.py

    Created 17 Nov 2017

    Functions to create and output a she_expected_shear_validation_statistics data product.

    Origin: OU-SHE -  Output from Calibration pipeline and input to Analysis pipeline;
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

from ..product_utility import init_placeholder_general, create_general_product_from_template


sample_file_name = 'SHE_PPT/sample_placeholder_general.xml'


def init():
    """
        Adds some extra functionality to the product
    """

    init_placeholder_general()


def create_dpd_she_expected_shear_validation_statistics(filename=None):
    """ Initialize a product of this type
    """

    return create_general_product_from_template(template_filename=sample_file_name,
                                                product_name="DpdShePlaceholderGeneral",
                                                filename=filename,)


# Add a useful alias
create_expected_shear_validation_statistics_product = create_dpd_she_expected_shear_validation_statistics
