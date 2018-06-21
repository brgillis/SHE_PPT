""" @file shear_bias_stats.py

    Created 21 June 2018

    Functions to create and output a shear bias statistics data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
"""

__updated__ = "2018-06-21"

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
import HeaderProvider.GenericHeaderProvider as HeaderProvider
# from SHE_PPT.file_io import read_xml_product, find_aux_file

# Temporary class definitions


class dpdShearBiasStatistics(object):

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return True


class ShearBiasStatistics(object):

    def __init__(self):
        self.BfdStatistics = None
        self.KsbStatistics = None
        self.LensMcStatistics = None
        self.MomentsMlStatistics = None
        self.RegaussStatistics = None


class MethodShearBiasStatistics(object):

    def __init__(self):
        self.G1Statistics = None
        self.G2Statistics = None


def init():
    """
        Adds some extra functionality to the dpdShearBiasStatistics product
    """

    binding_class = dpdShearBiasStatistics

    # Add the statistics methods

    binding_class.set_BFD_statistics = __set_BFD_statistics
    binding_class.get_BFD_statistics = __get_BFD_statistics

    binding_class.set_KSB_statistics = __set_KSB_statistics
    binding_class.get_KSB_statistics = __get_KSB_statistics

    binding_class.set_LensMC_statistics = __set_LensMC_statistics
    binding_class.get_LensMC_statistics = __get_LensMC_statistics

    binding_class.set_MomentsML_statistics = __set_MomentsML_statistics
    binding_class.get_MomentsML_statistics = __get_MomentsML_statistics

    binding_class.set_REGAUSS_statistics = __set_REGAUSS_statistics
    binding_class.get_REGAUSS_statistics = __get_REGAUSS_statistics

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_method_statistics = __get_method_statistics
    binding_class.set_method_statistics = __set_method_statistics

    binding_class.has_files = False


def __set_BFD_statistics(self, g1_statistics, g2_statistics):
    self.Data.BfdStatistics = create_bfd_statistics(
        g1_statistics, g2_statistics)
    return


def __get_BFD_statistics(self):
    if not hasattr(self.Data, "BfdStatistics"):
        return None, None
    elif self.Data.BfdStatistics is None:
        return None, None
    else:
        return (self.Data.BfdStatistics.G1Statistics,
                self.Data.BfdStatistics.G2Statistics,)


def __set_KSB_statistics(self, g1_statistics, g2_statistics):
    self.Data.KsbStatistics = create_ksb_statistics(
        g1_statistics, g2_statistics)
    return


def __get_KSB_statistics(self):
    if not hasattr(self.Data, "KsbStatistics"):
        return None, None
    elif self.Data.KsbStatistics is None:
        return None, None
    else:
        return (self.Data.KsbStatistics.G1Statistics,
                self.Data.KsbStatistics.G2Statistics,)


def __set_LensMC_statistics(self, g1_statistics, g2_statistics):
    self.Data.LensMcStatistics = create_lensmc_statistics(
        g1_statistics, g2_statistics)
    return


def __get_LensMC_statistics(self):
    if not hasattr(self.Data, "LensMcStatistics"):
        return None, None
    elif self.Data.LensMcStatistics is None:
        return None, None
    else:
        return (self.Data.LensMcStatistics.G1Statistics,
                self.Data.LensMcStatistics.G2Statistics,)


def __set_MomentsML_statistics(self, g1_statistics, g2_statistics):
    self.Data.MomentsMlStatistics = create_momentsml_statistics(
        g1_statistics, g2_statistics)
    return


def __get_MomentsML_statistics(self):
    if not hasattr(self.Data, "MomentsMlStatistics"):
        return None, None
    elif self.Data.MomentsMlStatistics is None:
        return None, None
    else:
        return (self.Data.MomentsMlStatistics.G1Statistics,
                self.Data.MomentsMlStatistics.G2Statistics,)


def __set_REGAUSS_statistics(self, g1_statistics, g2_statistics):
    self.Data.RegaussStatistics = create_regauss_statistics(
        g1_statistics, g2_statistics)
    return


def __get_REGAUSS_statistics(self):
    if not hasattr(self.Data, "RegaussStatistics"):
        return None, None
    elif self.Data.RegaussStatistics is None:
        return None, None
    else:
        return (self.Data.RegaussStatistics.G1Statistics,
                self.Data.RegaussStatistics.G2Statistics,)


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


def __get_method_statistics(self, method):

    if method == "KSB":
        return self.get_KSB_statistics()
    elif method == "LensMC":
        return self.get_LensMC_statistics()
    elif method == "MomentsML":
        return self.get_MomentsML_statistics()
    elif method == "REGAUSS":
        return self.get_REGAUSS_statistics()
    elif method == "BFD":
        return self.get_BFD_statistics()
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def __set_method_statistics(self, method, statistics):

    if method == "KSB":
        return self.set_KSB_statistics(statistics)
    elif method == "LensMC":
        return self.set_LensMC_statistics(statistics)
    elif method == "MomentsML":
        return self.set_MomentsML_statistics(statistics)
    elif method == "REGAUSS":
        return self.set_REGAUSS_statistics(statistics)
    elif method == "BFD":
        return self.set_BFD_statistics(statistics)
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def create_dpd_shear_bias_statistics(BFD_g1_statistics=None,
                                     BFD_g2_statistics=None,
                                     KSB_g1_statistics=None,
                                     KSB_g2_statistics=None,
                                     LensMC_g1_statistics=None,
                                     LensMC_g2_statistics=None,
                                     MomentsML_g1_statistics=None,
                                     MomentsML_g2_statistics=None,
                                     REGAUSS_g1_statistics=None,
                                     REGAUSS_g2_statistics=None):
    """
        @TODO fill in docstring
    """

    # dpd_shear_bias_stats = read_xml_product(
    #     find_aux_file(sample_file_name), allow_pickled=False)
    dpd_shear_bias_stats = dpdShearBiasStatistics()

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_shear_bias_stats.Header = HeaderProvider.createGenericHeader("SHE")
    dpd_shear_bias_stats.Data = ShearBiasStatistics()

    __set_BFD_statistics(
        dpd_shear_bias_stats, BFD_g1_statistics, BFD_g2_statistics)
    __set_KSB_statistics(
        dpd_shear_bias_stats, KSB_g1_statistics, KSB_g2_statistics)
    __set_LensMC_statistics(
        dpd_shear_bias_stats, LensMC_g1_statistics, LensMC_g2_statistics)
    __set_MomentsML_statistics(
        dpd_shear_bias_stats, MomentsML_g1_statistics, MomentsML_g2_statistics)
    __set_REGAUSS_statistics(
        dpd_shear_bias_stats, REGAUSS_g1_statistics, REGAUSS_g2_statistics)

    return dpd_shear_bias_stats

# Add a useful alias
create_shear_bias_statistics_product = create_dpd_shear_bias_statistics


def create_bfd_statistics(g1_statistics, g2_statistics):
    """
        @TODO fill in docstring
    """

    BFD_shear_estimates = MethodShearBiasStatistics()

    BFD_shear_estimates.G1Statistics = g1_statistics
    BFD_shear_estimates.G2Statistics = g2_statistics

    return BFD_shear_estimates


def create_ksb_statistics(g1_statistics, g2_statistics):
    """
        @TODO fill in docstring
    """

    KSB_shear_estimates = MethodShearBiasStatistics()

    KSB_shear_estimates.G1Statistics = g1_statistics
    KSB_shear_estimates.G2Statistics = g2_statistics

    return KSB_shear_estimates


def create_lensmc_statistics(g1_statistics, g2_statistics):
    """
        @TODO fill in docstring
    """

    LensMC_shear_estimates = MethodShearBiasStatistics()

    LensMC_shear_estimates.G1Statistics = g1_statistics
    LensMC_shear_estimates.G2Statistics = g2_statistics

    return LensMC_shear_estimates


def create_momentsml_statistics(g1_statistics, g2_statistics):
    """
        @TODO fill in docstring
    """

    MomentsML_shear_estimates = MethodShearBiasStatistics()

    MomentsML_shear_estimates.G1Statistics = g1_statistics
    MomentsML_shear_estimates.G2Statistics = g2_statistics

    return MomentsML_shear_estimates


def create_regauss_statistics(g1_statistics, g2_statistics):
    """
        @TODO fill in docstring
    """

    REGAUSS_shear_estimates = MethodShearBiasStatistics()

    REGAUSS_shear_estimates.G1Statistics = g1_statistics
    REGAUSS_shear_estimates.G2Statistics = g2_statistics

    return REGAUSS_shear_estimates
