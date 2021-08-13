""" @file she_object_id_list.py

    Created 14 Mar 2019

    Functions to create and output an she_object_id_list data product, which contains a list of the object IDs that
    we want to process in a given thread.

    Origin: OU-SHE
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
from ST_DataModelBindings.dpd.she.objectidlist_stub import dpdSheObjectIdList

from ..file_io import read_xml_product, find_aux_file


sample_file_name = "SHE_PPT/sample_object_id_list.xml"


def init():
    """
        Adds some extra functionality to the DpdSheObjectIdList product
    """

    binding_class = dpdSheObjectIdList

    binding_class.get_all_filenames = _get_all_filenames
    binding_class.get_id_list = _get_id_list
    binding_class.set_id_list = _set_id_list

    binding_class.has_files = False


def _get_all_filenames(self):

    all_filenames = []

    return all_filenames


def _get_id_list(self):

    return self.Data.ObjectIdList


def _set_id_list(self, l):

    self.Data.ObjectIdList = l


def create_dpd_she_object_id_list(id_list=None):
    """
        @TODO fill in docstring
    """

    dpd_she_object_id_list = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_object_id_list.Header = HeaderProvider.create_generic_header("DpdSheObjectIdList")  # FIXME

    if id_list:
        _set_id_list(dpd_she_object_id_list, id_list)
    else:
        _set_id_list(dpd_she_object_id_list, [])

    return dpd_she_object_id_list


# Add a useful alias
create_object_id_list_product = create_dpd_she_object_id_list
