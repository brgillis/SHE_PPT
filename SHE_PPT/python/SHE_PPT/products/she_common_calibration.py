""" @file she_common_calibration.py

    Created 13 Oct 2017

    Functions to create and output a common calibration data product.

    Origin: OU-SHE - Output from Calibration pipeline and input to Analysis pipeline;
    must be persistent in archive.
"""

__updated__ = "2021-08-16"

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

import ST_DM_DmUtils.DmUtils as dm_utils
from ST_DM_HeaderProvider import GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.she.commoncalibration_stub import dpdSheCommonCalibration
from ST_DataModelBindings.pro import she_stub as she_pro

from ..constants.shear_estimation_methods import ShearEstimationMethods
from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_binding_class, get_data_filename_from_product, set_data_filename_of_product

sample_file_name = "SHE_PPT/sample_common_calibration.xml"
product_type_name = "DpdSheCommonCalibration"


def init():
    """
        Adds some extra functionality to the dpdSheMeasurements product
    """

    binding_class = dpdSheCommonCalibration

    if not init_binding_class(binding_class,
                              init_function=create_dpd_she_common_calibration):
        return

    # Add the data file name methods

    binding_class.set_KSB_filename = _set_KSB_filename
    binding_class.get_KSB_filename = _get_KSB_filename

    binding_class.set_LensMC_filename = _set_LensMC_filename
    binding_class.get_LensMC_filename = _get_LensMC_filename

    binding_class.set_MomentsML_filename = _set_MomentsML_filename
    binding_class.get_MomentsML_filename = _get_MomentsML_filename

    binding_class.set_REGAUSS_filename = _set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = _get_REGAUSS_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.get_method_filename = _get_method_filename
    binding_class.set_method_filename = _set_method_filename

    binding_class.has_files = True


def _set_KSB_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "KsbCalibrationStorage"):
            self.Data.KsbCalibrationStorage = None
    else:
        if not hasattr(self.Data, "KsbCalibrationStorage") or self.Data.KsbCalibrationStorage is None:
            self.Data.KsbCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "KsbCalibrationStorage")


def _get_KSB_filename(self):
    if not hasattr(self.Data, "KsbCalibrationStorage") or self.Data.KsbCalibrationStorage is None:
        return None
    return get_data_filename_from_product(self, "KsbCalibrationStorage")


def _set_LensMC_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "LensMcCalibrationStorage"):
            self.Data.LensMcCalibrationStorage = None
    else:
        if not hasattr(self.Data, "LensMcCalibrationStorage") or self.Data.LensMcCalibrationStorage is None:
            self.Data.LensMcCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "LensMcCalibrationStorage")


def _get_LensMC_filename(self):
    if not hasattr(self.Data, "LensMcCalibrationStorage") or self.Data.LensMcCalibrationStorage is None:
        return None
    return get_data_filename_from_product(self, "LensMcCalibrationStorage")


def _set_MomentsML_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "MomentsMlCalibrationStorage"):
            self.Data.MomentsMlCalibrationStorage = None
    else:
        if not hasattr(self.Data, "MomentsMlCalibrationStorage") or self.Data.MomentsMlCalibrationStorage is None:
            self.Data.MomentsMlCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "MomentsMlCalibrationStorage")


def _get_MomentsML_filename(self):
    if not hasattr(self.Data, "MomentsMlCalibrationStorage") or self.Data.MomentsMlCalibrationStorage is None:
        return None
    return get_data_filename_from_product(self, "MomentsMlCalibrationStorage")


def _set_REGAUSS_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "RegaussCalibrationStorage"):
            self.Data.RegaussCalibrationStorage = None
    else:
        if not hasattr(self.Data, "RegaussCalibrationStorage") or self.Data.RegaussCalibrationStorage is None:
            self.Data.RegaussCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "RegaussCalibrationStorage")


def _get_REGAUSS_filename(self):
    if not hasattr(self.Data, "RegaussCalibrationStorage") or self.Data.RegaussCalibrationStorage is None:
        return None
    return get_data_filename_from_product(self, "RegaussCalibrationStorage")


def _get_all_filenames(self):

    all_filenames = [self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MomentsML_filename(),
                     self.get_REGAUSS_filename(), ]

    return all_filenames


def _get_method_filename(self, method):

    if method == ShearEstimationMethods.KSB:
        name = self.get_KSB_filename()
    elif method == ShearEstimationMethods.LENSMC:
        name = self.get_LensMC_filename()
    elif method == ShearEstimationMethods.MOMENTSML:
        name = self.get_MomentsML_filename()
    elif method == ShearEstimationMethods.REGAUSS:
        name = self.get_REGAUSS_filename()
    else:
        raise ValueError("Invalid method " + str(method) + ".")
    return name


def _set_method_filename(self, method, filename):

    if method == ShearEstimationMethods.KSB:
        name = self.set_KSB_filename(filename)
    elif method == ShearEstimationMethods.LENSMC:
        name = self.set_LensMC_filename(filename)
    elif method == ShearEstimationMethods.MOMENTSML:
        name = self.set_MomentsML_filename(filename)
    elif method == ShearEstimationMethods.REGAUSS:
        name = self.set_REGAUSS_filename(filename)
    else:
        raise ValueError("Invalid method " + str(method) + ".")
    return name


def create_dpd_she_common_calibration(KSB_filename=None,
                                      LensMC_filename=None,
                                      MomentsML_filename=None,
                                      REGAUSS_filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_common_calibration = read_xml_product(
        find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_common_calibration.Header = HeaderProvider.create_generic_header(product_type_name)

    _set_KSB_filename(dpd_she_common_calibration, KSB_filename)
    _set_LensMC_filename(dpd_she_common_calibration, LensMC_filename)
    _set_MomentsML_filename(dpd_she_common_calibration, MomentsML_filename)
    _set_REGAUSS_filename(dpd_she_common_calibration, REGAUSS_filename)

    return dpd_she_common_calibration


def create_calibration_storage(filename):
    """
        @TODO fill in docstring
    """

    calibration_storage = dm_utils.create_fits_storage(she_pro.sheCommonCalibrationFile,
                                                       filename,
                                                       "she.commonCalibration",
                                                       "8.0")

    return calibration_storage
