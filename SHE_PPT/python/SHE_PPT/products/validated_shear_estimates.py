""" @file validated_shear_estimates_product.py

    Created 17 Nov 2017

    Functions to create and output a validated_shear_estimates data product.

    Origin: OU-SHE - Output from Analysis pipeline; must be persistent in archive.
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

import HeaderProvider.GenericHeaderProvider as HeaderProvider
from EuclidDmBindings.dpd.she.raw.validatedshearmeasurement_stub import dpdValidatedShearMeasurement

from SHE_PPT.file_io import read_xml_product, find_aux_file

sample_file_name = "SHE_PPT/sample_validated_shear_measurements.xml"


def init():
    """
        Adds some extra functionality to the DpdSheAstrometry product
    """

    binding_class = dpdValidatedShearMeasurement

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __set_filename(self, filename):
    self.Data.ValidatedShearMeasurementFile.DataContainer.FileName = filename


def __get_filename(self):
    return self.Data.ValidatedShearMeasurementFile.DataContainer.FileName


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


def create_dpd_she_validated_shear_estimates(filename="default_filename.fits"):
    """
        @TODO fill in docstring
    """

    dpd_she_validated_shear_estimates = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_validated_shear_estimates.Header = HeaderProvider.createGenericHeader(
        "SHE")

    __set_filename(dpd_she_validated_shear_estimates, filename)

    return dpd_she_validated_shear_estimates

# Add a useful alias
create_validated_shear_estimates_product = create_dpd_she_validated_shear_estimates
