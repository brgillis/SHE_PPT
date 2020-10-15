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

__updated__ = "2020-10-15"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import pickle
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.intermediategeneral_stub import dpdSheIntermediateGeneral

sample_file_name = 'SHE_PPT/sample_intermediate_general.xml'


def init():
    """
        TODO: Fill in docstring

    """

    binding_class = dpdSheIntermediateGeneral

    # Add the data file name methods

    binding_class.set_filename = __set_data_filename
    binding_class.get_filename = __get_data_filename

    binding_class.set_data_filename = __set_data_filename
    binding_class.get_data_filename = __get_data_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage[0]")


def __get_data_filename(self):
    return get_data_filename_from_product(self, "DataStorage[0]")


def __get_all_filenames(self):

    all_filenames = [__get_data_filename(self)]

    return all_filenames


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

    dpd_she_simulated_catalog.Header = HeaderProvider.create_generic_header("SHE")

    if filename:
        __set_data_filename(dpd_she_simulated_catalog, filename)

    return dpd_she_simulated_catalog


# Add a useful alias
create_simulated_catalog_data_product = create_dpd_she_simulated_catalog
