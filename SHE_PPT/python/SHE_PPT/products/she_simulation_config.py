""" @file she_simulation_config_product.py

    Created 17 Nov 2017

    Functions to create and output a she_simulation_config data product.

    Origin: OU-SHE - Internal to Calibration pipeline.
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

__updated__ = "2020-10-15"

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product, init_intermediate_general
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider

sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'


def init():
    """
        Adds some extra functionality to the product
    """

    init_intermediate_general()

    return


def create_dpd_she_simulation_config(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_simulation_config = read_xml_product(
        find_aux_file(sample_file_name))

    # Set the data we don't need to empty
    dpd_she_simulation_config.Data.IntData = []
    dpd_she_simulation_config.Data.FloatData = []

    # Label the type in the StringData
    dpd_she_simulation_config.Data.StringData = ["TYPE:DpdSheSimulationConfig"]

    dpd_she_simulation_config.Header = HeaderProvider.create_generic_header("SHE")

    if filename:
        dpd_she_simulation_config.set_data_filename(filename)

    return dpd_she_simulation_config


# Add a useful alias
create_simulation_config_product = create_dpd_she_simulation_config
