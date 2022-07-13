""" @file she_simulated_catalog.py

    Created 17 Nov 2017

    Functions to create and output a simulated_catalog data product.

    Origin: OU-SHE - Internal to calibration pipeline.
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
# simulated_catalog.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

# Import dpdSheIntermediateObservationCatalog since it will be expected here
from ..product_utility import (ProductName, create_general_product_from_template, init_int_obs_cat)

sample_file_name = 'SHE_PPT/sample_intermediate_observation_catalog.xml'
product_type_name = "DpdSheSimulatedCatalog"


def init():
    """
        TODO: Fill in docstring

    """

    init_int_obs_cat(product_type_name=product_type_name,
                     init_function=create_dpd_she_simulated_catalog)


def create_dpd_she_simulated_catalog(filename=None):
    """ Initialize a product of this type
    """

    return create_general_product_from_template(template_filename=sample_file_name,
                                                product_type_name=product_type_name,
                                                general_product_type_name=ProductName.INT_OBS_CAT.value,
                                                filename=filename, )


# Add a useful alias
create_simulated_catalog_product = create_dpd_she_simulated_catalog
