""" @file mdb_mission_database.py

    Created 12 Apr 2023

    Function to add the get_all_filenames method to the MDB data product class. This is required for the tests to pass,
    but *should* have no practical use.
"""

__updated__ = "2023-04-13"

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
from ST_DataModelBindings.dpd.raw.mdb_stub import dpdMdbDataBase
from ..product_utility import init_no_files


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_no_files(binding_class=dpdMdbDataBase,
                          init_function=None)
