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

from ST_DataModelBindings.dpd.she.validatedmeasurements_stub import dpdSheValidatedMeasurements

from ..product_utility import (init_binding_class, create_measurements_product_from_template,
                               set_method_filename, get_method_filename,
                               set_KSB_filename, get_KSB_filename,
                               set_LensMC_filename, get_LensMC_filename,
                               set_MomentsML_filename, get_MomentsML_filename,
                               set_REGAUSS_filename, get_REGAUSS_filename,
                               get_all_filenames_methods)


sample_file_name = "SHE_PPT/sample_validated_shear_measurements.xml"


def init():
    """
        Adds some extra functionality to the dpdSheValidatedMeasurements product
    """

    binding_class = dpdSheValidatedMeasurements

    if not init_binding_class(binding_class):
        return

    # Add the data file name methods

    binding_class.set_KSB_filename = set_KSB_filename
    binding_class.get_KSB_filename = get_KSB_filename

    binding_class.set_LensMC_filename = set_LensMC_filename
    binding_class.get_LensMC_filename = get_LensMC_filename

    binding_class.set_MomentsML_filename = set_MomentsML_filename
    binding_class.get_MomentsML_filename = get_MomentsML_filename

    binding_class.set_REGAUSS_filename = set_REGAUSS_filename
    binding_class.get_REGAUSS_filename = get_REGAUSS_filename

    binding_class.get_all_filenames = get_all_filenames_methods

    binding_class.set_method_filename = set_method_filename
    binding_class.get_method_filename = get_method_filename

    binding_class.has_files = True


def create_dpd_she_validated_measurements(KSB_filename=None,
                                          LensMC_filename=None,
                                          MomentsML_filename=None,
                                          REGAUSS_filename=None,
                                          spatial_footprint=None):
    """ Create a product of this type.
    """

    return create_measurements_product_from_template(template_filename=sample_file_name,
                                                     product_name="DpdSheValidatedMeasurements",
                                                     KSB_filename=KSB_filename,
                                                     LensMC_filename=LensMC_filename,
                                                     MomentsML_filename=MomentsML_filename,
                                                     REGAUSS_filename=REGAUSS_filename,
                                                     spatial_footprint=spatial_footprint)


# Add a useful alias
create_she_validated_measurements_product = create_dpd_she_validated_measurements
