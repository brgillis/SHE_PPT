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

__updated__ = "2019-08-15"

from ST_DataModelBindings.dpd.sim.raw.starscatalogproduct_stub import dpdStarsCatalogProduct

from SHE_PPT.file_io import filename_include_data_subdir, data_subdir, len_data_subdir


def init():
    """
        Adds some extra functionality to the dpdStarsCatalogProduct class
    """
    binding_class = dpdStarsCatalogProduct

    # Add the data file name methods

    binding_class.get_data_filenames = __get_data_filenames
    binding_class.get_filenames = __get_data_filenames
    binding_class.get_all_filenames = __get_data_filenames

    binding_class.has_files = True

    return


def __get_data_filenames(self):

    data_filenames = []

    for star_catalog in self.Data.SetOfStarCatalogs:

        data_filename = star_catalog.StarCatalogFitsFile.DataContainer.FileName

        if filename_include_data_subdir:

            # Silently force the filename returned to start with "data/" regardless of whether the returned value does
            if data_filename[0:len_data_subdir] != data_subdir:
                data_filename = data_subdir + data_filename

        else:

            # Silently force the filename returned to NOT start with "data/" regardless of whether the returned value does
            if data_filename[0:len_data_subdir] == data_subdir:
                data_filename = data_filename.replace(data_subdir, "", 1)

        data_filenames.append(data_filename)

    return data_filenames
