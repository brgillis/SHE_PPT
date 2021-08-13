""" @file she_simulation_plan.py

    Created 17 Nov 2017

    Functions to create and output a she_simulation_plan data product.
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

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_intermediate_general


sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'


def init():
    """
        Adds some extra functionality to the product
    """

    init_intermediate_general()


def create_dpd_she_simulation_plan(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_simulation_plan = read_xml_product(
        find_aux_file(sample_file_name))

    # Set the data we don't need to empty
    dpd_she_simulation_plan.Data.IntData = []
    dpd_she_simulation_plan.Data.FloatData = []

    # Label the type in the StringData
    dpd_she_simulation_plan.Data.StringData = ["TYPE:DpdSheSimulationPlan"]

    dpd_she_simulation_plan.Header = HeaderProvider.create_generic_header("DpdSheIntermediateGeneral")

    if filename:
        dpd_she_simulation_plan.set_data_filename(filename)

    return dpd_she_simulation_plan


# Add a useful alias
create_simulation_plan_product = create_dpd_she_simulation_plan
