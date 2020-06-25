""" @file she_common_calibration.py

    Created 13 Oct 2017

    Functions to create and output a calibration parameters data product.

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

__updated__ = "2020-06-25"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME
import pickle

from SHE_PPT.file_io import read_xml_product, find_aux_file, get_data_filename_from_product, set_data_filename_of_product


def init():
    """
        Adds some extra functionality to the DpdSheCommonCalibration product
    """

    # binding_class = she_dpd.DpdSheCommonCalibration # @FIXME
    binding_class = DpdSheCommonCalibration

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
    set_data_filename_of_product(self, filename, "BFDCalibrationParameters")


def __get_BFD_filename(self):
    return get_data_filename_from_product(self, "BFDCalibrationParameters")


def __set_KSB_filename(self, filename):
    set_data_filename_of_product(self, filename, "KSBCalibrationParameters")


def __get_KSB_filename(self):
    return get_data_filename_from_product(self, "KSBCalibrationParameters")


def __set_LensMC_filename(self, filename):
    set_data_filename_of_product(self, filename, "LensMCCalibrationParameters")


def __get_LensMC_filename(self):
    return get_data_filename_from_product(self, "LensMCCalibrationParameters")


def __set_MomentsML_filename(self, filename):
    set_data_filename_of_product(self, filename, "MomentsMLCalibrationParameters")


def __get_MomentsML_filename(self):
    return get_data_filename_from_product(self, "MomentsMLCalibrationParameters")


def __set_REGAUSS_filename(self, filename):
    set_data_filename_of_product(self, filename, "REGAUSSCalibrationParameters")


def __get_REGAUSS_filename(self):
    return get_data_filename_from_product(self, "REGAUSSCalibrationParameters")


def __get_all_filenames(self):

    all_filenames = [self.get_BFD_filename(),
                     self.get_KSB_filename(),
                     self.get_LensMC_filename(),
                     self.get_MomentsML_filename(),
                     self.get_REGAUSS_filename(), ]

    return all_filenames


def __get_method_filename(self, method):

    if method == "BFD":
        return self.get_BFD_filename()
    elif method == "KSB":
        return self.get_KSB_filename()
    elif method == "LensMC":
        return self.get_LensMC_filename()
    elif method == "MomentsML":
        return self.get_MomentsML_filename()
    elif method == "REGAUSS":
        return self.get_REGAUSS_filename()
    else:
        raise ValueError("Invalid method " + str(method) + ".")


class DpdSheCommonCalibration:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class SheCommonCalibration:  # @FIXME

    def __init__(self):
        self.BFDCalibrationParameters = None
        self.KSBCalibrationParameters = None
        self.LensMCCalibrationParameters = None
        self.MomentsMLCalibrationParameters = None
        self.REGAUSSCalibrationParameters = None


class DataContainer:  # @FIXME

    def __init__(self):
        self.FileName = None
        self.filestatus = None


class SheBfdCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class SheKsbCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class SheLensMcCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class SheMomentsMlCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


class SheRegaussCalibrationParameters:  # @FIXME

    def __init__(self):
        self.format = None
        self.version = None
        self.DataContainer = None


def create_dpd_she_common_calibration(BFD_filename=None,
                                          KSB_filename=None,
                                          LensMC_filename=None,
                                          MomentsML_filename=None,
                                          REGAUSS_filename=None):
    """
        @TODO fill in docstring
    """

    # dpd_calibration_parameters = she_dpd.DpdSheCommonCalibration() #
    # @FIXME
    dpd_calibration_parameters = DpdSheCommonCalibration()

    # dpd_calibration_parameters.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    dpd_calibration_parameters.Header = "SHE"

    dpd_calibration_parameters.Data = create_she_common_calibration(BFD_filename,
                                                                        KSB_filename,
                                                                        LensMC_filename,
                                                                        MomentsML_filename,
                                                                        REGAUSS_filename)

    return dpd_calibration_parameters


# Add a useful alias
create_calibration_parameters_product = create_dpd_she_common_calibration


def create_she_common_calibration(BFD_filename=None,
                                      KSB_filename=None,
                                      LensMC_filename=None,
                                      MomentsML_filename=None,
                                      REGAUSS_filename=None):
    """
        @TODO fill in docstring
    """

    # calibration_parameters = she_dpd.SheCommonCalibration() # @FIXME
    calibration_parameters = SheCommonCalibration()

    # Read these in from
    calibration_parameters.BFDCalibrationParameters = create_she_bfd_calibration_parameters(
        BFD_filename)

    calibration_parameters.KSBCalibrationParameters = create_she_KSB_calibration_parameters(
        KSB_filename)

    calibration_parameters.LensMCCalibrationParameters = create_she_LensMC_calibration_parameters(
        LensMC_filename)

    calibration_parameters.MomentsMLCalibrationParameters = create_she_MomentsML_calibration_parameters(
        MomentsML_filename)

    calibration_parameters.REGAUSSCalibrationParameters = create_she_REGAUSS_calibration_parameters(
        REGAUSS_filename)

    return calibration_parameters


def create_she_bfd_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """

    # bfd_calibration_parameters = she_dpd.SheBfdCalibrationParameters() #
    # @FIXME
    bfd_calibration_parameters = SheBfdCalibrationParameters()

    bfd_calibration_parameters.format = "UNDEFINED"
    bfd_calibration_parameters.version = "0.0"

    bfd_calibration_parameters.DataContainer = DataContainer()
    bfd_calibration_parameters.DataContainer.FileName = filename
    bfd_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return bfd_calibration_parameters


def create_she_KSB_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """

    # KSB_calibration_parameters = she_dpd.SheKsbCalibrationParameters() #
    # @FIXME
    KSB_calibration_parameters = SheKsbCalibrationParameters()

    KSB_calibration_parameters.format = "UNDEFINED"
    KSB_calibration_parameters.version = "0.0"

    KSB_calibration_parameters.DataContainer = DataContainer()
    KSB_calibration_parameters.DataContainer.FileName = filename
    KSB_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return KSB_calibration_parameters


def create_she_LensMC_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """

    # LensMC_calibration_parameters = she_dpd.SheLensMcCalibrationParameters()
    # # @FIXME
    LensMC_calibration_parameters = SheLensMcCalibrationParameters()

    LensMC_calibration_parameters.format = "UNDEFINED"
    LensMC_calibration_parameters.version = "0.0"

    LensMC_calibration_parameters.DataContainer = DataContainer()
    LensMC_calibration_parameters.DataContainer.FileName = filename
    LensMC_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return LensMC_calibration_parameters


def create_she_MomentsML_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """

    # MomentsML_calibration_parameters =
    # she_dpd.SheMomentsMlCalibrationParameters() # @FIXME
    MomentsML_calibration_parameters = SheMomentsMlCalibrationParameters()

    MomentsML_calibration_parameters.format = "UNDEFINED"
    MomentsML_calibration_parameters.version = "0.0"

    MomentsML_calibration_parameters.DataContainer = DataContainer()
    MomentsML_calibration_parameters.DataContainer.FileName = filename
    MomentsML_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return MomentsML_calibration_parameters


def create_she_REGAUSS_calibration_parameters(filename):
    """
        @TODO fill in docstring
    """

    # REGAUSS_calibration_parameters =
    # she_dpd.SheRegaussCalibrationParameters() # @FIXME
    REGAUSS_calibration_parameters = SheRegaussCalibrationParameters()

    REGAUSS_calibration_parameters.format = "UNDEFINED"
    REGAUSS_calibration_parameters.version = "0.0"

    REGAUSS_calibration_parameters.DataContainer = DataContainer()
    REGAUSS_calibration_parameters.DataContainer.FileName = filename
    REGAUSS_calibration_parameters.DataContainer.filestatus = "PROPOSED"

    return REGAUSS_calibration_parameters
