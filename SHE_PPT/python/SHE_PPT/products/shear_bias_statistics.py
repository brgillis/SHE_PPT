""" @file shear_bias_statistics.py

    Created 22 June 2018

    Functions to create and output a shear bias statistics data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
"""

__updated__ = "2019-07-15"

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

# from EuclidDmBindings.dpd.she.raw.shearmeasurement_stub import dpdShearBiasStatistics
# import HeaderProvider.GenericHeaderProvider as HeaderProvider
# from SHE_PPT.file_io import read_xml_product, find_aux_file

# Temporary class definitions

import SHE_PPT


class dpdShearBiasStatistics(object):

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return True


class ShearBiasStatistics(object):  # @FIXME

    def __init__(self):
        self.BfdBiasMeasurements = None
        self.KsbBiasMeasurements = None
        self.LensMcBiasMeasurements = None
        self.MomentsMlBiasMeasurements = None
        self.RegaussBiasMeasurements = None


class MethodShearBiasStatistics(object):  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


def init():
    """
        Adds some extra functionality to the dpdShearBiasStatistics product
    """

    binding_class = dpdShearBiasStatistics

    # Add the statistics methods

    binding_class.set_BFD_bias_statistics_filename = __set_BFD_bias_statistics_filename
    binding_class.get_BFD_bias_statistics_filename = __get_BFD_bias_statistics_filename

    binding_class.set_KSB_bias_statistics_filename = __set_KSB_bias_statistics_filename
    binding_class.get_KSB_bias_statistics_filename = __get_KSB_bias_statistics_filename

    binding_class.set_LensMC_bias_statistics_filename = __set_LensMC_bias_statistics_filename
    binding_class.get_LensMC_bias_statistics_filename = __get_LensMC_bias_statistics_filename

    binding_class.set_MomentsML_bias_statistics_filename = __set_MomentsML_bias_statistics_filename
    binding_class.get_MomentsML_bias_statistics_filename = __get_MomentsML_bias_statistics_filename

    binding_class.set_REGAUSS_bias_statistics_filename = __set_REGAUSS_bias_statistics_filename
    binding_class.get_REGAUSS_bias_statistics_filename = __get_REGAUSS_bias_statistics_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_method_bias_statistics_filename = __get_method_bias_statistics_filename
    binding_class.set_method_bias_statistics_filename = __set_method_bias_statistics_filename

    binding_class.has_files = True


def __set_BFD_bias_statistics_filename(self, filename):
    self.Data.BfdBiasMeasurements = create_method_shear_bias_statistics(filename)
    return


def __get_BFD_bias_statistics_filename(self):

    if not hasattr(self.Data, "BfdBiasMeasurements"):
        return None

    filename = self.Data.BfdBiasMeasurements.DataContainer.Filename

    if filename == "None":
        return None
    else:
        return filename


def __set_KSB_bias_statistics_filename(self, filename):
    self.Data.KsbBiasMeasurements = create_method_shear_bias_statistics(filename)
    return


def __get_KSB_bias_statistics_filename(self):

    if not hasattr(self.Data, "KsbBiasMeasurements"):
        return None

    filename = self.Data.KsbBiasMeasurements.DataContainer.Filename

    if filename == "None":
        return None
    else:
        return filename


def __set_LensMC_bias_statistics_filename(self, filename):
    self.Data.LensMcBiasMeasurements = create_method_shear_bias_statistics(filename)
    return


def __get_LensMC_bias_statistics_filename(self):

    if not hasattr(self.Data, "LensMcBiasMeasurements"):
        return None

    filename = self.Data.LensMcBiasMeasurements.DataContainer.Filename

    if filename == "None":
        return None
    else:
        return filename


def __set_MomentsML_bias_statistics_filename(self, filename):
    self.Data.MomentsMlBiasMeasurements = create_method_shear_bias_statistics(filename)
    return


def __get_MomentsML_bias_statistics_filename(self):

    if not hasattr(self.Data, "MomentsMlBiasMeasurements"):
        return None

    filename = self.Data.MomentsMlBiasMeasurements.DataContainer.Filename

    if filename == "None":
        return None
    else:
        return filename


def __set_REGAUSS_bias_statistics_filename(self, filename):
    self.Data.RegaussBiasMeasurements = create_method_shear_bias_statistics(filename)
    return


def __get_REGAUSS_bias_statistics_filename(self):

    if not hasattr(self.Data, "RegaussBiasMeasurements"):
        return None

    filename = self.Data.RegaussBiasMeasurements.DataContainer.Filename

    if filename == "None":
        return None
    else:
        return filename


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


def __get_method_bias_statistics_filename(self, method):

    switcher = {"KSB": self.get_KSB_bias_statistics_filename,
                "LensMC": self.get_LensMC_bias_statistics_filename,
                "MomentsML": self.get_MomentsML_bias_statistics_filename,
                "REGAUSS": self.get_REGAUSS_bias_statistics_filename,
                "BFD": self.get_BFD_bias_statistics_filename, }

    try:
        return switcher[method]()
    except KeyError:
        ValueError("Invalid method " + str(method) + ".")


def __set_method_bias_statistics_filename(self, method, filename):

    switcher = {"KSB": self.set_KSB_bias_statistics_filename,
                "LensMC": self.set_LensMC_bias_statistics_filename,
                "MomentsML": self.set_MomentsML_bias_statistics_filename,
                "REGAUSS": self.set_REGAUSS_bias_statistics_filename,
                "BFD": self.set_BFD_bias_statistics_filename, }

    try:
        return switcher[method](filename)
    except KeyError:
        ValueError("Invalid method " + str(method) + ".")


def create_dpd_shear_bias_statistics(BFD_bias_statistics_filename=None,
                                     KSB_bias_statistics_filename=None,
                                     LensMC_bias_statistics_filename=None,
                                     MomentsML_bias_statistics_filename=None,
                                     REGAUSS_bias_statistics_filename=None,):
    """
        @TODO fill in docstring
    """

    # dpd_shear_bias_stats = read_xml_product(
    #     find_aux_file(sample_file_name), allow_pickled=False)
    dpd_shear_bias_stats = dpdShearBiasStatistics()

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    # dpd_shear_bias_stats.Header = HeaderProvider.createGenericHeader("SHE")
    dpd_shear_bias_stats.Header = "SHE"
    dpd_shear_bias_stats.Data = ShearBiasStatistics()

    dpd_shear_bias_stats.set_BFD_bias_statistics_filename(BFD_bias_statistics_filename)
    dpd_shear_bias_stats.set_KSB_bias_statistics_filename(KSB_bias_statistics_filename)
    dpd_shear_bias_stats.set_LensMC_bias_statistics_filename(LensMC_bias_statistics_filename)
    dpd_shear_bias_stats.set_MomentsML_bias_statistics_filename(MomentsML_bias_statistics_filename)
    dpd_shear_bias_stats.set_REGAUSS_bias_statistics_filename(REGAUSS_bias_statistics_filename)

    return dpd_shear_bias_stats


# Add a useful alias

create_shear_bias_statistics_product = create_dpd_shear_bias_statistics


# Creation functions

def create_method_shear_bias_statistics(filename):

    method_shear_estimates = MethodShearBiasStatistics()

    method_shear_estimates.format = "fits"
    method_shear_estimates.version = SHE_PPT.__version__
    method_shear_estimates.DataContainer = create_data_container(filename)

    return method_shear_estimates


def create_data_container(filename):

    data_container = DataContainer()

    data_container.FileName = filename
    data_container.filestatus = "PROPOSED"

    return data_container
