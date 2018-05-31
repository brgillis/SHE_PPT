""" @file shear_estimates_product.py

    Created 9 Oct 2017

    Functions to create and output a shear estimates data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import HeaderProvider.GenericHeaderProvider as HeaderProvider

import EuclidDmBindings.pro.she_stub as she_pro
from EuclidDmBindings.dpd.she.shearmeasurement_stub import DpdShearMeasurement

from EuclidDmBindings.sys.dss_stub import dataContainer

def init():
    """
        Adds some extra functionality to the DpdShearEstimates product
    """

    binding_class = DpdShearMeasurement

    # Add the data file name methods

    binding_class.set_BFD_filename = __set_BFD_filename
    binding_class.get_BFD_filename = __get_BFD_filename

    binding_class.set_KSB_filename = __set_KSB_filename
    binding_class.get_KSB_filename = __get_KSB_filename

    binding_class.set_LensMC_filename = __set_LensMC_filename
    binding_class.get_LensMC_filename = __get_LensMC_filename

    binding_class.set_MomentsML_filename = __set_MomentsML_filename
    binding_class.get_MomentsML_filename = __get_MomentsML_filename

    binding_class.set_REGAUSS_filename = __set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = __get_REGAUSS_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_method_filename = __get_method_filename

    binding_class.has_files = True

def __set_BFD_filename(self, filename):
    self.Data.BFDShearEstimates.DataContainer.FileName = filename

def __get_BFD_filename(self):
    return self.Data.BFDShearEstimates.DataContainer.FileName

def __set_KSB_filename(self, filename):
    self.Data.KSBShearEstimates.DataContainer.FileName = filename

def __get_KSB_filename(self):
    return self.Data.KSBShearEstimates.DataContainer.FileName

def __set_LensMC_filename(self, filename):
    self.Data.LensMCShearEstimates.DataContainer.FileName = filename

def __get_LensMC_filename(self):
    return self.Data.LensMCShearEstimates.DataContainer.FileName

def __set_MomentsML_filename(self, filename):
    self.Data.MomentsMLShearEstimates.DataContainer.FileName = filename

def __get_MomentsML_filename(self):
    return self.Data.MomentsMLShearEstimates.DataContainer.FileName

def __set_REGAUSS_filename(self, filename):
    self.Data.REGAUSSShearEstimates.DataContainer.FileName = filename

def __get_REGAUSS_filename(self):
    return self.Data.REGAUSSShearEstimates.DataContainer.FileName

def __get_all_filenames(self):

    all_filenames = [self.get_BFD_filename(),
                     self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MomentsML_filename(),
                     self.get_REGAUSS_filename(), ]

    return all_filenames

def __get_method_filename(self, method):

    if method == "KSB":
        return self.get_KSB_filename()
    elif method == "LensMC":
        return self.get_LensMC_filename()
    elif method == "MomentsML":
        return self.get_MomentsML_filename()
    elif method == "REGAUSS":
        return self.get_REGAUSS_filename()
    elif method == "BFD":
        return self.get_BFD_filename()
    else:
        raise ValueError("Invalid method " + str(method) + ".")

def create_dpd_shear_estimates(BFD_filename = "",
                               KSB_filename = "",
                               LensMC_filename = "",
                               MomentsML_filename = "",
                               REGAUSS_filename = ""):
    """
        @TODO fill in docstring
    """

    dpd_shear_estimates = DpdShearMeasurement()

    dpd_shear_estimates.Header = HeaderProvider.createGenericHeader("SHE")

    dpd_shear_estimates.Data = create_shear_estimates(BFD_filename,
                                                       KSB_filename,
                                                       LensMC_filename,
                                                       MomentsML_filename,
                                                       REGAUSS_filename)

    return dpd_shear_estimates

# Add a useful alias
create_shear_estimates_product = create_dpd_shear_estimates

def create_shear_estimates(BFD_filename,
                           KSB_filename,
                           LensMC_filename,
                           MomentsML_filename,
                           REGAUSS_filename):
    """
        @TODO fill in docstring
    """

    shear_estimates = she_pro.shearMeasurement()

    shear_estimates.BfdMoments = create_BFD_shear_estimates(BFD_filename)

    shear_estimates.KsbShearEstimates = create_KSB_shear_estimates(KSB_filename)

    shear_estimates.LensMcShearEstimates = create_LensMC_shear_estimates(LensMC_filename)

    shear_estimates.MomentsMlShearEstimates = create_MomentsML_shear_estimates(MomentsML_filename)

    shear_estimates.RegaussShearEstimates = create_REGAUSS_shear_estimates(REGAUSS_filename)

    return shear_estimates

def create_BFD_shear_estimates(filename):
    """
        @TODO fill in docstring
    """

    BFD_shear_estimates = she_pro.bfdMoments()

    BFD_shear_estimates.format = "she.bfdMoments"
    BFD_shear_estimates.version = "0.1"

    BFD_shear_estimates.DataContainer = dataContainer()
    BFD_shear_estimates.DataContainer.FileName = filename
    BFD_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return BFD_shear_estimates

def create_KSB_shear_estimates(filename):
    """
        @TODO fill in docstring
    """

    KSB_shear_estimates = she_pro.ksbShearEstimates()

    KSB_shear_estimates.format = "she.ksbShearEstimates"
    KSB_shear_estimates.version = "0.1"

    KSB_shear_estimates.DataContainer = dataContainer()
    KSB_shear_estimates.DataContainer.FileName = filename
    KSB_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return KSB_shear_estimates

def create_LensMC_shear_estimates(filename):
    """
        @TODO fill in docstring
    """

    LensMC_shear_estimates = she_pro.lensMcShearEstimates()

    LensMC_shear_estimates.format = "she.lensMcShearEstimates"
    LensMC_shear_estimates.version = "0.1"

    LensMC_shear_estimates.DataContainer = dataContainer()
    LensMC_shear_estimates.DataContainer.FileName = filename
    LensMC_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return LensMC_shear_estimates

def create_MomentsML_shear_estimates(filename):
    """
        @TODO fill in docstring
    """

    MomentsML_shear_estimates = she_pro.momentsMlShearEstimates()

    MomentsML_shear_estimates.format = "she.momentsMlShearEstimates"
    MomentsML_shear_estimates.version = "0.1"

    MomentsML_shear_estimates.DataContainer = dataContainer()
    MomentsML_shear_estimates.DataContainer.FileName = filename
    MomentsML_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return MomentsML_shear_estimates

def create_REGAUSS_shear_estimates(filename):
    """
        @TODO fill in docstring
    """

    REGAUSS_shear_estimates = she_pro.regaussShearEstimates()

    REGAUSS_shear_estimates.format = "she.regaussShearEstimates"
    REGAUSS_shear_estimates.version = "0.1"

    REGAUSS_shear_estimates.DataContainer = dataContainer()
    REGAUSS_shear_estimates.DataContainer.FileName = filename
    REGAUSS_shear_estimates.DataContainer.filestatus = "PROPOSED"

    return REGAUSS_shear_estimates
