""" @file she_validated_measurements.py

    Created 9 Oct 2017

    Functions to create and output a shear estimates data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
"""

__updated__ = "2021-08-13"

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
from ST_DataModelBindings.dpd.she.validatedmeasurements_stub import dpdSheValidatedMeasurements
from ST_DataModelBindings.pro import she_stub as she_pro

from ..constants.shear_estimation_methods import ShearEstimationMethods
from ..file_io import read_xml_product, find_aux_file
from ..product_utility import (get_data_filename_from_product, set_data_filename_of_product,
                               init_binding_class)


sample_file_name = "SHE_PPT/sample_validated_shear_measurements.xml"


def init():
    """
        Adds some extra functionality to the dpdSheValidatedMeasurements product
    """

    binding_class = dpdSheValidatedMeasurements

    if not init_binding_class(binding_class):
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
        if hasattr(self.Data, "KsbShearMeasurements"):
            self.Data.KsbShearMeasurements = None
    else:
        if not hasattr(self.Data, "KsbShearMeasurements") or self.Data.KsbShearMeasurements is None:
            self.Data.KsbShearMeasurements = create_ksb_estimates(filename)
        set_data_filename_of_product(self, filename, "KsbShearMeasurements.DataStorage")


def _get_KSB_filename(self):
    if not hasattr(self.Data, "KsbShearMeasurements") or self.Data.KsbShearMeasurements is None:
        return None
    return get_data_filename_from_product(self, "KsbShearMeasurements.DataStorage")


def _set_LensMC_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "LensMcShearMeasurements"):
            self.Data.LensMcShearMeasurements = None
    else:
        if not hasattr(self.Data, "LensMcShearMeasurements") or self.Data.LensMcShearMeasurements is None:
            self.Data.LensMcShearMeasurements = create_lensmc_estimates(filename)
        set_data_filename_of_product(self, filename, "LensMcShearMeasurements.DataStorage")


def _get_LensMC_filename(self):
    if not hasattr(self.Data, "LensMcShearMeasurements") or self.Data.LensMcShearMeasurements is None:
        return None
    return get_data_filename_from_product(self, "LensMcShearMeasurements.DataStorage")


def _set_MomentsML_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "MomentsMlShearMeasurements"):
            self.Data.MomentsMlShearMeasurements = None
    else:
        if not hasattr(self.Data, "MomentsMlShearMeasurements") or self.Data.MomentsMlShearMeasurements is None:
            self.Data.MomentsMlShearMeasurements = create_momentsml_estimates(filename)
        set_data_filename_of_product(self, filename, "MomentsMlShearMeasurements.DataStorage")


def _get_MomentsML_filename(self):
    if not hasattr(self.Data, "MomentsMlShearMeasurements") or self.Data.MomentsMlShearMeasurements is None:
        return None
    return get_data_filename_from_product(self, "MomentsMlShearMeasurements.DataStorage")


def _set_REGAUSS_filename(self, filename):
    if filename is None:
        if hasattr(self.Data, "RegaussShearMeasurements"):
            self.Data.RegaussShearMeasurements = None
    else:
        if not hasattr(self.Data, "RegaussShearMeasurements") or self.Data.RegaussShearMeasurements is None:
            self.Data.RegaussShearMeasurements = create_regauss_estimates(filename)
        set_data_filename_of_product(self, filename, "RegaussShearMeasurements.DataStorage")


def _get_REGAUSS_filename(self):
    if not hasattr(self.Data, "RegaussShearMeasurements") or self.Data.RegaussShearMeasurements is None:
        return None
    return get_data_filename_from_product(self, "RegaussShearMeasurements.DataStorage")


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


def create_dpd_she_validated_measurements(KSB_filename=None,
                                          LensMC_filename=None,
                                          MomentsML_filename=None,
                                          REGAUSS_filename=None,
                                          spatial_footprint=None):
    """
        @TODO fill in docstring
    """

    dpd_she_validated_measurements = read_xml_product(
        find_aux_file(sample_file_name))

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_validated_measurements.Header = HeaderProvider.create_generic_header("DpdSheValidatedMeasurements")

    _set_KSB_filename(dpd_she_validated_measurements, KSB_filename)
    _set_LensMC_filename(dpd_she_validated_measurements, LensMC_filename)
    _set_MomentsML_filename(dpd_she_validated_measurements, MomentsML_filename)
    _set_REGAUSS_filename(dpd_she_validated_measurements, REGAUSS_filename)
    if spatial_footprint is not None:
        dpd_she_validated_measurements.set_spatial_footprint(spatial_footprint)

    return dpd_she_validated_measurements


# Add a useful alias
create_she_validated_measurements_product = create_dpd_she_validated_measurements


def create_ksb_estimates(filename):
    """
        @TODO fill in docstring
    """

    KSB_shear_estimates = she_pro.sheKsbMeasurements()

    KSB_shear_estimates.DataStorage = dm_utils.create_fits_storage(she_pro.sheKsbMeasurementsFile,
                                                                   filename,
                                                                   "she.ksbMeasurements",
                                                                   "8.0")
    KSB_shear_estimates.Valid = "VALID"

    return KSB_shear_estimates


def create_lensmc_estimates(filename):
    """
        @TODO fill in docstring
    """

    LensMC_shear_estimates = she_pro.sheLensMcMeasurements()

    LensMC_shear_estimates.DataStorage = dm_utils.create_fits_storage(she_pro.sheLensMcMeasurementsFile,
                                                                      filename,
                                                                      "she.lensMcMeasurements",
                                                                      "8.0")
    LensMC_shear_estimates.Valid = "VALID"

    return LensMC_shear_estimates


def create_momentsml_estimates(filename):
    """
        @TODO fill in docstring
    """

    MomentsML_shear_estimates = she_pro.sheMomentsMlMeasurements()

    MomentsML_shear_estimates.DataStorage = dm_utils.create_fits_storage(she_pro.sheMomentsMlMeasurementsFile,
                                                                         filename,
                                                                         "she.momentsMlMeasurements",
                                                                         "8.0")
    MomentsML_shear_estimates.Valid = "VALID"

    return MomentsML_shear_estimates


def create_regauss_estimates(filename):
    """
        @TODO fill in docstring
    """

    REGAUSS_shear_estimates = she_pro.sheRegaussMeasurements()

    REGAUSS_shear_estimates.DataStorage = dm_utils.create_fits_storage(she_pro.sheRegaussMeasurementsFile,
                                                                       filename,
                                                                       "she.regaussMeasurements",
                                                                       "8.0")
    REGAUSS_shear_estimates.Valid = "VALID"

    return REGAUSS_shear_estimates
