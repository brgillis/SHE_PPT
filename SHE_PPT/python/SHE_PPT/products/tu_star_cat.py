""" @file tu_star_cat.py

    Created 10 May 2019

    Code to help with reading in and using a DpdStarCatalogProduct

    Origin: OU-SIM - Star Catalog Product
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

from ST_DataModelBindings.dpd.sim.raw.starscatalogproduct_stub import dpdStarsCatalogProduct

from ..product_utility import get_data_filename_from_product


def init():
    """
        Adds some extra functionality to the dpdStarsCatalogProduct class
    """
    binding_class = dpdStarsCatalogProduct

    # Add the data file name methods

    binding_class.get_data_filename = __get_data_filename
    binding_class.get_filename = __get_data_filename
    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True

    return


def __get_data_filename(self):
    return get_data_filename_from_product(self, "StarCatalog.DataStorage")


def __get_all_filenames(self):

    all_filenames = [self.get_data_filename(), ]

    return all_filenames
