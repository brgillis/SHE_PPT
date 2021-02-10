""" @file she_analysis_config.py

    Created 24 Nov 2017

    Functions to create and output a analysis_config data product.

    Origin: OU-SHE - Needs to be implemented in data model. Input to Analysis pipeline;
    must be persistent in archive.
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

__updated__ = "2020-08-12"

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.analysisconfig_stub import dpdSheAnalysisConfig

sample_file_name = "SHE_PPT/sample_analysis_config.xml"


def init():
    """
        Initialisers for LensMC training
    """

    binding_class = dpdSheAnalysisConfig

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename
    binding_class.set_data_filename = __set_filename
    binding_class.get_data_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def __get_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def __get_all_filenames(self):

    all_filenames = [self.get_filename()]

    return all_filenames


def create_dpd_she_analysis_config(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_analysis_config = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_analysis_config.Header = HeaderProvider.create_generic_header("SHE")

    if filename:
        __set_filename(dpd_she_analysis_config, filename)
    return dpd_she_analysis_config


# Add a useful alias
create_analysis_config_data_product = create_dpd_she_analysis_config
