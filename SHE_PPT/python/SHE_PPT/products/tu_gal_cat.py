""" @file tu_gal_cat.py

    Created 10 May 2019

    Code to help with reading in and using a DpdGalaxyCatalogProduct

    Origin: OU-SIM - Galaxy Catalog Product
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

from ST_DataModelBindings.dpd.sim.raw.galaxycatalogproduct_stub import dpdGalaxyCatalogProduct

from ..product_utility import get_data_filename_from_product, get_all_filenames_just_data


def init():
    """
        Adds some extra functionality to the dpdGalaxyCatalogProduct class
    """
    binding_class = dpdGalaxyCatalogProduct

    # Add the data file name methods

    binding_class.get_data_filename = _get_data_filename
    binding_class.get_filename = _get_data_filename
    binding_class.get_all_filenames = get_all_filenames_just_data

    binding_class.has_files = True


def _get_data_filename(self):
    return get_data_filename_from_product(self, "GalaxyCatalog.DataStorage")
