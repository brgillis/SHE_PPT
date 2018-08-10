""" @file lensmc_training_data_product.py

    Created 24 Nov 2017

    Functions to create and output a lensmc_training_data data product.

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

import HeaderProvider.GenericHeaderProvider as HeaderProvider 
from SHE_PPT.file_io import read_xml_product, find_aux_file
from EuclidDmBindings.dpd.she.shearlensmctraining_stub import dpdShearLensMCTraining
import pickle

sample_file_name = "SHE_PPT/sample_lensmc_training.xml"




def init():
    """
        Initialisers for LensMC training
    """

    # binding_class = she_dpd.DpdSheLensMCTrainingDataProduct # @FIXME
    binding_class = dpdShearLensMCTraining

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_filename(self, filename):
    self.Data.ShearLensMCTrainingFile.DataContainer.FileName = filename


def __get_filename(self):
    return self.Data.ShearLensMCTrainingFile.DataContainer.FileName


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


class DpdSheLensMCTrainingDataProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheLensMCTrainingDataProduct:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def create_dpd_she_lensmc_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_she_lensmc_training_data = she_dpd.DpdSheLensMCTrainingDataProduct()
    # # FIXME
    dpd_she_lensmc_training_data = read_xml_product(
        find_aux_file(sample_file_name))

    dpd_she_lensmc_training_data.Header = HeaderProvider.createGenericHeader("SHE") 

    #dpd_she_lensmc_training_data.Data = create_she_lensmc_training_data(
    #    filename)

    if filename:
        __set_filename(dpd_she_lensmc_training_data,filename)
    return dpd_she_lensmc_training_data

# Add a useful alias
create_lensmc_training_data_product = create_dpd_she_lensmc_training_data


def create_she_lensmc_training_data(filename=None):
    """
        @TODO fill in docstring
    """

    # she_lensmc_training_data = she_dpd.SheLensMCTrainingDataProduct() #
    # @FIXME
    she_lensmc_training_data = SheLensMCTrainingDataProduct()

    she_lensmc_training_data.format = "UNDEFINED"
    she_lensmc_training_data.version = "0.0"

    she_lensmc_training_data.DataContainer = DataContainer()
    she_lensmc_training_data.DataContainer.FileName = filename
    she_lensmc_training_data.DataContainer.filestatus = "PROPOSED"

    return she_lensmc_training_data
