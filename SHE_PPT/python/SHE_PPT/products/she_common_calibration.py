""" @file she_common_calibration.py

    Created 13 Oct 2017

    Functions to create and output a common calibration data product.

    Origin: OU-SHE - Output from Calibration pipeline and input to Analysis pipeline;
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

__updated__ = "2020-10-15"

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product
import ST_DM_DmUtils.DmUtils as dm_utils
from ST_DM_HeaderProvider import GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.commoncalibration_stub import dpdSheCommonCalibration
from ST_DataModelBindings.pro import she_stub as she_pro
from ST_DataModelBindings.sys.dss_stub import dataContainer

sample_file_name = "SHE_PPT/sample_common_calibration.xml"


def init():
    """
        Adds some extra functionality to the dpdSheMeasurements product
    """

    binding_class = dpdSheCommonCalibration

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
    binding_class.set_method_filename = __set_method_filename

    binding_class.has_files = True


def __set_BFD_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "BfdCalibrationStorage"):
            self.Data.BfdCalibrationStorage = None
    else:
        if not hasattr(self.Data, "BfdCalibrationStorage") or self.Data.BfdCalibrationStorage is None:
            self.Data.BfdCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "BfdCalibrationStorage")
    return


def __get_BFD_filename(self):
    if not hasattr(self.Data, "BfdCalibrationStorage") or self.Data.BfdCalibrationStorage is None:
        return None
    else:
        return get_data_filename_from_product(self, "BfdCalibrationStorage")


def __set_KSB_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "KsbCalibrationStorage"):
            self.Data.KsbCalibrationStorage = None
    else:
        if not hasattr(self.Data, "KsbCalibrationStorage") or self.Data.KsbCalibrationStorage is None:
            self.Data.KsbCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "KsbCalibrationStorage")
    return


def __get_KSB_filename(self):
    if not hasattr(self.Data, "KsbCalibrationStorage") or self.Data.KsbCalibrationStorage is None:
        return None
    else:
        return get_data_filename_from_product(self, "KsbCalibrationStorage")


def __set_LensMC_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "LensMcCalibrationStorage"):
            self.Data.LensMcCalibrationStorage = None
    else:
        if not hasattr(self.Data, "LensMcCalibrationStorage") or self.Data.LensMcCalibrationStorage is None:
            self.Data.LensMcCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "LensMcCalibrationStorage")
    return


def __get_LensMC_filename(self):
    if not hasattr(self.Data, "LensMcCalibrationStorage") or self.Data.LensMcCalibrationStorage is None:
        return None
    else:
        return get_data_filename_from_product(self, "LensMcCalibrationStorage")


def __set_MomentsML_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "MomentsMlCalibrationStorage"):
            self.Data.MomentsMlCalibrationStorage = None
    else:
        if not hasattr(self.Data, "MomentsMlCalibrationStorage") or self.Data.MomentsMlCalibrationStorage is None:
            self.Data.MomentsMlCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "MomentsMlCalibrationStorage")
    return


def __get_MomentsML_filename(self):
    if not hasattr(self.Data, "MomentsMlCalibrationStorage") or self.Data.MomentsMlCalibrationStorage is None:
        return None
    else:
        return get_data_filename_from_product(self, "MomentsMlCalibrationStorage")


def __set_REGAUSS_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "RegaussCalibrationStorage"):
            self.Data.RegaussCalibrationStorage = None
    else:
        if not hasattr(self.Data, "RegaussCalibrationStorage") or self.Data.RegaussCalibrationStorage is None:
            self.Data.RegaussCalibrationStorage = create_calibration_storage(filename)
        set_data_filename_of_product(self, filename, "RegaussCalibrationStorage")
    return


def __get_REGAUSS_filename(self):
    if not hasattr(self.Data, "RegaussCalibrationStorage") or self.Data.RegaussCalibrationStorage is None:
        return None
    else:
        return get_data_filename_from_product(self, "RegaussCalibrationStorage")


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


def __set_method_filename(self, method, filename):

    if method == "KSB":
        return self.set_KSB_filename(filename)
    elif method == "LensMC":
        return self.set_LensMC_filename(filename)
    elif method == "MomentsML":
        return self.set_MomentsML_filename(filename)
    elif method == "REGAUSS":
        return self.set_REGAUSS_filename(filename)
    elif method == "BFD":
        return self.set_BFD_filename(filename)
    else:
        raise ValueError("Invalid method " + str(method) + ".")


def create_dpd_she_common_calibration(BFD_filename=None,
                                      KSB_filename=None,
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
    dpd_she_common_calibration.Header = HeaderProvider.create_generic_header("SHE")

    __set_BFD_filename(dpd_she_common_calibration, BFD_filename)
    __set_KSB_filename(dpd_she_common_calibration, KSB_filename)
    __set_LensMC_filename(dpd_she_common_calibration, LensMC_filename)
    __set_MomentsML_filename(dpd_she_common_calibration, MomentsML_filename)
    __set_REGAUSS_filename(dpd_she_common_calibration, REGAUSS_filename)

    return dpd_she_common_calibration


# Add a useful alias
create_common_calibration_product = create_dpd_she_common_calibration


def create_calibration_storage(filename):
    """
        @TODO fill in docstring
    """

    calibration_storage = dm_utils.create_fits_storage(she_pro.sheCommonCalibrationFile,
                                                       filename,
                                                       "she.commonCalibration",
                                                       "8.0")

    return calibration_storage
