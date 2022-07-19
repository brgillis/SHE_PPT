""" @file tu_star_cat.py

    Created 10 May 2019

    Code to help with reading in and using a DpdStarCatalogProduct

    Origin: OU-SIM - Star Catalog Product
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

from ST_DataModelBindings.dpd.sim.raw.starscatalogproduct_stub import dpdStarsCatalogProduct
from ..product_utility import get_all_filenames_just_data, get_data_filename_from_product


def init():
    """
        Adds some extra functionality to the dpdStarsCatalogProduct class
    """
    binding_class = dpdStarsCatalogProduct

    # Add the data file name methods

    binding_class.get_data_filename = _get_data_filename
    binding_class.get_filename = _get_data_filename
    binding_class.get_all_filenames = get_all_filenames_just_data

    binding_class.has_files = True

    binding_class.init_function = None


def _get_data_filename(self):
    return get_data_filename_from_product(self, "StarCatalog.DataStorage")
