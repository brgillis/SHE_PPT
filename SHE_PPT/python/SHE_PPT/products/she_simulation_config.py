""" @file she_simulation_config_product.py

    Created 17 Nov 2017

    Functions to create and output a she_simulation_config data product.

    Origin: OU-SHE - Internal to Calibration pipeline.
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

# Import dpdSheIntermediateGeneral since it will be expected here
from ..product_utility import (ProductName, create_general_product_from_template, init_intermediate_general)

sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'
product_type_name = "DpdSheSimulationConfig"


def init():
    """
        Adds some extra functionality to the product
    """

    init_intermediate_general(product_type_name=product_type_name,
                              init_function=create_dpd_she_simulation_config)


def create_dpd_she_simulation_config(filename=None):
    """ Initialize a product of this type
    """

    return create_general_product_from_template(template_filename=sample_file_name,
                                                product_type_name=product_type_name,
                                                general_product_type_name=ProductName.INT_GENERAL.value,
                                                filename=filename, )


# Add a useful alias
create_simulation_config_product = create_dpd_she_simulation_config
