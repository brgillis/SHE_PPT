""" @file regauss_training_data_product.py

    Created 24 Nov 2017

    Functions to create and output a regauss_training_data data product.

    Origin: OU-SHE - Needs to be implemented in data model. Output from Calibration pipeline
    and input to Analysis pipeline; must be persistent in archive.
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

import pickle

from ST_DataModelBindings.dpd.she.raw.regausstraining_stub import dpdSheRegaussTraining
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product

sample_file_name = 'SHE_PPT/sample_regauss_training.xml'


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdSheRegaussTraining

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

    all_filenames = [self.get_data_filename()]

    return all_filenames


class DpdSheREGAUSSTrainingDataProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheREGAUSSTrainingDataProduct:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_regauss_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_regauss_training_data =
    # she_dpd.DpdSheREGAUSSTrainingDataProduct() # FIXME
    dpd_she_regauss_training_data = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    dpd_she_regauss_training_data.Header = HeaderProvider.create_generic_header("SHE")  # FIXME

    # dpd_she_regauss_training_data.Data = create_she_regauss_training_data(
    #    filename)

    if filename:
        __set_filename(dpd_she_regauss_training_data, filename)

    return dpd_she_regauss_training_data


# Add a useful alias
create_regauss_training_data_product = create_dpd_she_regauss_training_data


def create_she_regauss_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # she_regauss_training_data = she_dpd.SheREGAUSSTrainingDataProduct() #
    # @FIXME
    she_regauss_training_data = SheREGAUSSTrainingDataProduct()

    she_regauss_training_data.format = "UNDEFINED"
    she_regauss_training_data.version = "0.0"

    she_regauss_training_data.DataContainer = DataContainer()
    she_regauss_training_data.DataContainer.FileName = filename
    she_regauss_training_data.DataContainer.filestatus = "PROPOSED"

    return she_regauss_training_data
