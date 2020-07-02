""" @file she_psf_field_parameters.py

    Created 24 Nov 2017

    Functions to create and output a psf_field_parameters data product.

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

__updated__ = "2020-06-30"

import pickle

from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.psffieldparameters_stub import dpdShePsfFieldParameters

sample_file_name = "SHE_PPT/sample_psf_field_parameters.xml"


def init():
    """
        Initialisers for LensMC training
    """

    binding_class = dpdShePsfFieldParameters

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


class DpdShePsfFieldParameters:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class ShePsfFieldParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_psf_field_parameters(filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_psf_field_parameters = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_psf_field_parameters.Header = HeaderProvider.create_generic_header("SHE")

    if filename:
        __set_filename(dpd_she_psf_field_parameters, filename)
    return dpd_she_psf_field_parameters


# Add a useful alias
create_psf_field_parameters_data_product = create_dpd_she_psf_field_parameters


def create_she_psf_field_parameters(filename=None):
    """
        @TODO fill in docstring
    """

    she_psf_field_parameters = ShePsfFieldParameters()

    she_psf_field_parameters.format = "she.psfFieldParameters"
    she_psf_field_parameters.version = "8.0"

    she_psf_field_parameters.DataContainer = DataContainer()
    she_psf_field_parameters.DataContainer.FileName = filename
    she_psf_field_parameters.DataContainer.filestatus = "PROPOSED"

    return she_psf_field_parameters
