""" @file she_reconciled_measurements.py

    Created 22 July 2020

    Functions to create and output a shear estimates data product.

    Origin: OU-SHE - Internal to Analysis and Calibration pipelines.
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

from ST_DataModelBindings.dpd.she.reconciledmeasurements_stub import dpdSheReconciledMeasurements

from ..product_utility import init_method_files, create_measurements_product_from_template


sample_file_name = "SHE_PPT/sample_reconciled_shear_measurements.xml"


def init():
    """
        Adds some extra functionality to the dpdSheReconciledMeasurements product
    """

    init_method_files(binding_class=dpdSheReconciledMeasurements,
                      init_function=create_dpd_she_reconciled_measurements)


def create_dpd_she_reconciled_measurements(KSB_filename=None,
                                           LensMC_filename=None,
                                           MomentsML_filename=None,
                                           REGAUSS_filename=None,
                                           spatial_footprint=None):
    """ Create a product of this type.
    """

    return create_measurements_product_from_template(template_filename=sample_file_name,
                                                     product_type_name="DpdSheReconciledMeasurements",
                                                     KSB_filename=KSB_filename,
                                                     LensMC_filename=LensMC_filename,
                                                     MomentsML_filename=MomentsML_filename,
                                                     REGAUSS_filename=REGAUSS_filename,
                                                     spatial_footprint=spatial_footprint)


# Add a useful alias
create_she_reconciled_measurements_product = create_dpd_she_reconciled_measurements
