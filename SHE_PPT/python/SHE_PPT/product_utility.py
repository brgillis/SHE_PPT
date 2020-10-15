""" @file product_utility.py

    Created 15 October 2020

    Utility functions related to data products
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

from SHE_PPT.logging import getLogger
from SHE_PPT.utility import run_only_once, get_nested_attr
from ST_DataModelBindings.dpd.she.intermediategeneral_stub import dpdSheIntermediateGeneral


logger = getLogger(__name__)

filename_include_data_subdir = False
data_subdir = "data/"
len_data_subdir = len(data_subdir)


def get_data_filename_from_product(p, attr_name=None):
    """ Helper function to get a data filename from a product, adjusting for whether to include the data subdir as desired.
    """

    if attr_name is None or attr_name == 0:
        data_filename = p.Data.DataContainer.FileName
    elif attr_name == -1:
        data_filename = p.Data.FileName
    else:
        data_filename = get_nested_attr(p.Data, attr_name).DataContainer.FileName

    if data_filename is None:
        return None

    # Silently force the filename returned to start with "data/" regardless of
    # whether the returned value does, unless it's absolute
    if len(data_filename) > 0 and (data_filename[0:len_data_subdir] == data_subdir or data_filename[0] == "/"):
        return data_filename
    else:
        return data_subdir + data_filename


def set_data_filename_of_product(p, data_filename, attr_name=None):
    """ Helper function to set a data filename of a product, adjusting for whether to include the data subdir as desired.
    """

    if data_filename is not None and len(data_filename) > 0 and data_filename[0] != "/":
        if filename_include_data_subdir:

            # Silently force the filename returned to start with "data/" regardless of
            # whether the returned value does
            if data_filename[0:len_data_subdir] != data_subdir:
                data_filename = data_subdir + data_filename

        else:

            # Silently force the filename returned to NOT start with "data/"
            # regardless of whether the returned value does
            if data_filename[0:len_data_subdir] == data_subdir:
                data_filename = data_filename.replace(data_subdir, "", 1)

    if attr_name is None or attr_name == 0:
        p.Data.DataContainer.FileName = data_filename
    elif attr_name == -1:
        p.Data.FileName = data_filename
    else:
        get_nested_attr(p.Data, attr_name).DataContainer.FileName = data_filename

    return


def __set_intermediate_general_data_filename(self, filename, i=0):
    set_data_filename_of_product(self, filename, f"DataStorage[{i}]")


def __get_intermediate_general_data_filename(self, i=0):
    return get_data_filename_from_product(self, f"DataStorage[{i}]")


def __get_all_intermediate_general_filenames(self):

    all_filenames = [__get_data_filename(self)]

    return all_filenames


@run_only_once
def init_intermediate_general():
    binding_class = dpdSheIntermediateGeneral

    # Add the data file name methods

    binding_class.set_filename = __set_intermediate_general_data_filename
    binding_class.get_filename = __get_intermediate_general_data_filename

    binding_class.set_data_filename = __set_intermediate_general_data_filename
    binding_class.get_data_filename = __get_intermediate_general_data_filename

    binding_class.get_all_filenames = __get_all_intermediate_general_filenames

    binding_class.has_files = True

    return


def __set_placeholder_general_data_filename(self, filename, i=0):
    set_data_filename_of_product(self, filename, f"DataStorage[{i}]")


def __get_placeholder_general_data_filename(self, i=0):
    return get_data_filename_from_product(self, f"DataStorage[{i}]")


def __get_all_placeholder_general_filenames(self):

    all_filenames = [__get_data_filename(self)]

    return all_filenames


@run_only_once
def init_placeholder_general():
    binding_class = dpdShePlaceholderGeneral

    # Add the data file name methods

    binding_class.set_filename = __set_placeholder_general_data_filename
    binding_class.get_filename = __get_placeholder_general_data_filename

    binding_class.set_data_filename = __set_placeholder_general_data_filename
    binding_class.get_data_filename = __get_placeholder_general_data_filename

    binding_class.get_all_filenames = __get_all_placeholder_general_filenames

    binding_class.has_files = True

    return
