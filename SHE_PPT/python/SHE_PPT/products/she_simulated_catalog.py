""" @file she_simulated_catalog.py

    Created 17 Nov 2017

    Functions to create and output a simulated_catalog data product.

    Origin: OU-SHE - Internal to calibration pipeline.
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# simulated_catalog.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2021-06-10"

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_intermediate_observation_catalog


sample_file_name = 'SHE_PPT/sample_intermediate_observation_catalog.xml'


def init():
    """
        TODO: Fill in docstring

    """

    init_intermediate_observation_catalog()



def create_dpd_she_simulated_catalog(filename="None"):
    """
        @TODO fill in docstring
    """

    dpd_she_simulated_catalog = read_xml_product(
        find_aux_file(sample_file_name))

    # Set the data we don't need to empty
    dpd_she_simulated_catalog.Data.IntData = []
    dpd_she_simulated_catalog.Data.FloatData = []

    # Label the type in the StringData
    dpd_she_simulated_catalog.Data.StringData = ["TYPE:DpdSheSimulatedCatalog"]

    dpd_she_simulated_catalog.Header = HeaderProvider.create_generic_header("DpdSheIntermediateObservationCatalog")

    if filename:
        dpd_she_simulated_catalog.set_data_filename(filename)

    return dpd_she_simulated_catalog


# Add a useful alias
create_simulated_catalog_product = create_dpd_she_simulated_catalog
