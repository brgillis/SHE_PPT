""" @file bfd_training_data_product.py

    Created 24 Nov 2017

    Functions to create and output a bfd_training_data data product.

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

from ST_DataModelBindings.dpd.she.shearbfdtraining_stub import dpdShearBFDTraining
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_bfd_training.xml"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    # binding_class = she_dpd.DpdSheBFDTrainingDataProduct # @FIXME
    binding_class = dpdShearBFDTraining

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename

    binding_class.set_data_filename = __set_filename
    binding_class.get_data_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = True

    return


def __set_filename(self, filename):
    set_data_filename_of_product(self, filename, "ShearBFDTrainingFile")


def __get_filename(self):
    return get_data_filename_from_product(self, "ShearBFDTrainingFile")


def __get_all_filenames(self):

    all_filenames = [__get_filename(self)]

    return all_filenames


# class DpdSheBFDTrainingDataProduct:  # @FIXME

#    def __init__(self):
#        self.Header = None
#        self.Data = None

#    def validateBinding(self):
#        return False


# class SheBFDTrainingDataProduct:  # @FIXME

#    def __init__(self):
#        self.format = None
#        self.version = None
#        self.DataContainer = None


# class DataContainer:  # @FIXME

#    def __init__(self):
#        self.FileName = None
#        self.filestatus = None


def create_dpd_she_bfd_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_bfd_training_data = she_dpd.DpdSheBFDTrainingDataProduct() #
    # FIXME
    dpd_she_bfd_training_data = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_bfd_training_data.Header = HeaderProvider.createGenericHeader("SHE")

    if filename:
        __set_filename(dpd_she_bfd_training_data, filename)

    return dpd_she_bfd_training_data


# Add a useful alias
create_bfd_training_data_product = create_dpd_she_bfd_training_data


def create_she_bfd_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # she_bfd_training_data = she_dpd.SheBFDTrainingDataProduct() # @FIXME
    she_bfd_training_data = SheBFDTrainingDataProduct()

    she_bfd_training_data.format = "UNDEFINED"
    she_bfd_training_data.version = "0.0"

    she_bfd_training_data.DataContainer = DataContainer()
    she_bfd_training_data.DataContainer.FileName = filename
    she_bfd_training_data.DataContainer.filestatus = "PROPOSED"

    return she_bfd_training_data
