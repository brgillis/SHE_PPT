""" @file shear_bias_measurements.py

    Created 22 June 2018

    Functions to create and output a shear bias statistics data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
"""

__updated__ = "2018-06-22"

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

# from EuclidDmBindings.dpd.she.raw.shearmeasurement_stub import dpdShearBiasMeasurements
# import HeaderProvider.GenericHeaderProvider as HeaderProvider
# from SHE_PPT.file_io import read_xml_product, find_aux_file

# Temporary class definitions


class dpdShearBiasMeasurements(object):

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return True


class ShearBiasMeasurements(object):

    def __init__(self):
        self.BfdBiasMeasurements = None
        self.KsbBiasMeasurements = None
        self.LensMcBiasMeasurements = None
        self.MomentsMlBiasMeasurements = None
        self.RegaussBiasMeasurements = None


class MethodShearBiasMeasurements(object):

    def __init__(self):
        self.G1BiasMeasurements = None
        self.G2BiasMeasurements = None


def init():
    """
        Adds some extra functionality to the dpdShearBiasMeasurements product
    """

    binding_class = dpdShearBiasMeasurements

    # Add the statistics methods

    binding_class.set_BFD_bias_measurements = __set_BFD_bias_measurements
    binding_class.get_BFD_bias_measurements = __get_BFD_bias_measurements

    binding_class.set_KSB_bias_measurements = __set_KSB_bias_measurements
    binding_class.get_KSB_bias_measurements = __get_KSB_bias_measurements

    binding_class.set_LensMC_bias_measurements = __set_LensMC_bias_measurements
    binding_class.get_LensMC_bias_measurements = __get_LensMC_bias_measurements

    binding_class.set_MomentsML_bias_measurements = __set_MomentsML_bias_measurements
    binding_class.get_MomentsML_bias_measurements = __get_MomentsML_bias_measurements

    binding_class.set_REGAUSS_bias_measurements = __set_REGAUSS_bias_measurements
    binding_class.get_REGAUSS_bias_measurements = __get_REGAUSS_bias_measurements

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_method_bias_measurements = __get_method_bias_measurements
    binding_class.set_method_bias_measurements = __set_method_bias_measurements

    binding_class.has_files = False


def __set_BFD_bias_measurements(self, g1_bias_measurements, g2_bias_measurements):
    self.Data.BfdBiasMeasurements = create_bfd_bias_measurements(
        g1_bias_measurements, g2_bias_measurements)
    return


def __get_BFD_bias_measurements(self):
    if not hasattr(self.Data, "BfdBiasMeasurements"):
        return None, None
    elif self.Data.BfdBiasMeasurements is None:
        return None, None
    else:
        return (self.Data.BfdBiasMeasurements.G1BiasMeasurements,
                self.Data.BfdBiasMeasurements.G2BiasMeasurements,)


def __set_KSB_bias_measurements(self, g1_bias_measurements, g2_bias_measurements):
    self.Data.KsbBiasMeasurements = create_ksb_bias_measurements(
        g1_bias_measurements, g2_bias_measurements)
    return


def __get_KSB_bias_measurements(self):
    if not hasattr(self.Data, "KsbBiasMeasurements"):
        return None, None
    elif self.Data.KsbBiasMeasurements is None:
        return None, None
    else:
        return (self.Data.KsbBiasMeasurements.G1BiasMeasurements,
                self.Data.KsbBiasMeasurements.G2BiasMeasurements,)


def __set_LensMC_bias_measurements(self, g1_bias_measurements, g2_bias_measurements):
    self.Data.LensMcBiasMeasurements = create_lensmc_bias_measurements(
        g1_bias_measurements, g2_bias_measurements)
    return


def __get_LensMC_bias_measurements(self):
    if not hasattr(self.Data, "LensMcBiasMeasurements"):
        return None, None
    elif self.Data.LensMcBiasMeasurements is None:
        return None, None
    else:
        return (self.Data.LensMcBiasMeasurements.G1BiasMeasurements,
                self.Data.LensMcBiasMeasurements.G2BiasMeasurements,)


def __set_MomentsML_bias_measurements(self, g1_bias_measurements, g2_bias_measurements):
    self.Data.MomentsMlBiasMeasurements = create_momentsml_bias_measurements(
        g1_bias_measurements, g2_bias_measurements)
    return


def __get_MomentsML_bias_measurements(self):
    if not hasattr(self.Data, "MomentsMlBiasMeasurements"):
        return None, None
    elif self.Data.MomentsMlBiasMeasurements is None:
        return None, None
    else:
        return (self.Data.MomentsMlBiasMeasurements.G1BiasMeasurements,
                self.Data.MomentsMlBiasMeasurements.G2BiasMeasurements,)


def __set_REGAUSS_bias_measurements(self, g1_bias_measurements, g2_bias_measurements):
    self.Data.RegaussBiasMeasurements = create_regauss_bias_measurements(
        g1_bias_measurements, g2_bias_measurements)
    return


def __get_REGAUSS_bias_measurements(self):
    if not hasattr(self.Data, "RegaussBiasMeasurements"):
        return None, None
    elif self.Data.RegaussBiasMeasurements is None:
        return None, None
    else:
        return (self.Data.RegaussBiasMeasurements.G1BiasMeasurements,
                self.Data.RegaussBiasMeasurements.G2BiasMeasurements,)


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


def __get_method_bias_measurements(self, method):

    if method == "KSB":
        return self.get_KSB_bias_measurements()
    elif method == "LensMC":
        return self.get_LensMC_bias_measurements()
    elif method == "MomentsML":
        return self.get_MomentsML_bias_measurements()
    elif method == "REGAUSS":
        return self.get_REGAUSS_bias_measurements()
    elif method == "BFD":
        return self.get_BFD_bias_measurements()
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def __set_method_bias_measurements(self, method, g1_bias_measurements, g2_bias_measurements):

    if method == "KSB":
        return self.set_KSB_bias_measurements(g1_bias_measurements, g2_bias_measurements)
    elif method == "LensMC":
        return self.set_LensMC_bias_measurements(g1_bias_measurements, g2_bias_measurements)
    elif method == "MomentsML":
        return self.set_MomentsML_bias_measurements(g1_bias_measurements, g2_bias_measurements)
    elif method == "REGAUSS":
        return self.set_REGAUSS_bias_measurements(g1_bias_measurements, g2_bias_measurements)
    elif method == "BFD":
        return self.set_BFD_bias_measurements(g1_bias_measurements, g2_bias_measurements)
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def create_dpd_shear_bias_measurements(BFD_g1_bias_measurements=None,
                                       BFD_g2_bias_measurements=None,
                                       KSB_g1_bias_measurements=None,
                                       KSB_g2_bias_measurements=None,
                                       LensMC_g1_bias_measurements=None,
                                       LensMC_g2_bias_measurements=None,
                                       MomentsML_g1_bias_measurements=None,
                                       MomentsML_g2_bias_measurements=None,
                                       REGAUSS_g1_bias_measurements=None,
                                       REGAUSS_g2_bias_measurements=None):
    """
        @TODO fill in docstring
    """

    # dpd_shear_bias_stats = read_xml_product(
    #     find_aux_file(sample_file_name), allow_pickled=False)
    dpd_shear_bias_stats = dpdShearBiasMeasurements()

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    # dpd_shear_bias_stats.Header = HeaderProvider.createGenericHeader("SHE")
    dpd_shear_bias_stats.Header = "SHE"
    dpd_shear_bias_stats.Data = ShearBiasMeasurements()

    __set_BFD_bias_measurements(
        dpd_shear_bias_stats, BFD_g1_bias_measurements, BFD_g2_bias_measurements)
    __set_KSB_bias_measurements(
        dpd_shear_bias_stats, KSB_g1_bias_measurements, KSB_g2_bias_measurements)
    __set_LensMC_bias_measurements(
        dpd_shear_bias_stats, LensMC_g1_bias_measurements, LensMC_g2_bias_measurements)
    __set_MomentsML_bias_measurements(
        dpd_shear_bias_stats, MomentsML_g1_bias_measurements, MomentsML_g2_bias_measurements)
    __set_REGAUSS_bias_measurements(
        dpd_shear_bias_stats, REGAUSS_g1_bias_measurements, REGAUSS_g2_bias_measurements)

    return dpd_shear_bias_stats

# Add a useful alias
create_shear_bias_measurements_product = create_dpd_shear_bias_measurements


def create_bfd_bias_measurements(g1_bias_measurements, g2_bias_measurements):
    """
        @TODO fill in docstring
    """

    BFD_shear_estimates = MethodShearBiasMeasurements()

    BFD_shear_estimates.G1BiasMeasurements = g1_bias_measurements
    BFD_shear_estimates.G2BiasMeasurements = g2_bias_measurements

    return BFD_shear_estimates


def create_ksb_bias_measurements(g1_bias_measurements, g2_bias_measurements):
    """
        @TODO fill in docstring
    """

    KSB_shear_estimates = MethodShearBiasMeasurements()

    KSB_shear_estimates.G1BiasMeasurements = g1_bias_measurements
    KSB_shear_estimates.G2BiasMeasurements = g2_bias_measurements

    return KSB_shear_estimates


def create_lensmc_bias_measurements(g1_bias_measurements, g2_bias_measurements):
    """
        @TODO fill in docstring
    """

    LensMC_shear_estimates = MethodShearBiasMeasurements()

    LensMC_shear_estimates.G1BiasMeasurements = g1_bias_measurements
    LensMC_shear_estimates.G2BiasMeasurements = g2_bias_measurements

    return LensMC_shear_estimates


def create_momentsml_bias_measurements(g1_bias_measurements, g2_bias_measurements):
    """
        @TODO fill in docstring
    """

    MomentsML_shear_estimates = MethodShearBiasMeasurements()

    MomentsML_shear_estimates.G1BiasMeasurements = g1_bias_measurements
    MomentsML_shear_estimates.G2BiasMeasurements = g2_bias_measurements

    return MomentsML_shear_estimates


def create_regauss_bias_measurements(g1_bias_measurements, g2_bias_measurements):
    """
        @TODO fill in docstring
    """

    REGAUSS_shear_estimates = MethodShearBiasMeasurements()

    REGAUSS_shear_estimates.G1BiasMeasurements = g1_bias_measurements
    REGAUSS_shear_estimates.G2BiasMeasurements = g2_bias_measurements

    return REGAUSS_shear_estimates
