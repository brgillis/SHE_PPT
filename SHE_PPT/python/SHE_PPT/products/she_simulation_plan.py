""" @file she_simulation_plan.py

    Created 17 Nov 2017

    Functions to create and output a she_simulation_plan data product.
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

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider

from ..product_utility import init_intermediate_general, create_general_product_from_template


sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'


def init():
    """
        Adds some extra functionality to the product
    """

    init_intermediate_general(init_function=create_dpd_she_simulation_plan)


def create_dpd_she_simulation_plan(filename=None):
    """ Initialize a product of this type
    """

    return create_general_product_from_template(template_filename=sample_file_name,
                                                product_type_name="DpdSheIntermediateGeneral",
                                                filename=filename,)


# Add a useful alias
create_simulation_plan_product = create_dpd_she_simulation_plan
