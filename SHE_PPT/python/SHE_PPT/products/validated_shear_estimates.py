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

__updated__ = "2020-01-28"

from SHE_PPT.file_io import (read_xml_product, find_aux_file, get_data_filename_from_product,
                             set_data_filename_of_product)
from ST_DM_HeaderProvider import GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.raw.validatedshearmeasurement_stub import dpdValidatedShearMeasurement


sample_file_name = "SHE_PPT/sample_validated_shear_measurements.xml"


def init():
    """
        ValidatedShearMeasurement
    """

    binding_class = dpdValidatedShearMeasurement

    # Add the data file name methods

    binding_class.set_filename = __set_filename
    binding_class.get_filename = __get_filename

    binding_class.set_data_filename = __set_filename
    binding_class.get_data_filename = __get_filename

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.get_spatial_footprint = __get_spatial_footprint
    binding_class.set_spatial_footprint = __set_spatial_footprint

    binding_class.has_files = True

    return


def __set_filename(self, filename):
    set_data_filename_of_product(self, filename, "ValidatedShearMeasurementFile")


def __get_filename(self):
    return get_data_filename_from_product(self, "ValidatedShearMeasurementFile")


def __get_all_filenames(self):

    all_filenames = [self.get_filename()]

    return all_filenames


def __set_spatial_footprint(self, p):
    """ Set the spatial footprint. p can be either the spatial footprint, or
        another product which has a spatial footprint defined.
    """

    # Figure out how the spatial footprint was passed to us
    if isinstance(p, str):
        # If we got a filepath, read it in and apply this function to the read-in product
        return __set_spatial_footprint(self, read_xml_product(p))
    elif isinstance(p, polygonType):
        poly = p
    elif hasattr(p, "Polygon"):
        poly = p.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "ImgSpatialFootprint"):
        poly = p.Data.ImgSpatialFootprint.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "CatalogCoverage"):
        poly = p.Data.CatalogCoverage.SpatialCoverage.Polygon
    else:
        raise TypeError("For set_spatial_footprint, must be provided a spatial footprint, a product which has it, " +
                        "or the path to such a product. Received: " + str(type(p)))

    self.Data.CatalogCoverage.SpatialCoverage.Polygon = poly

    return


def __get_spatial_footprint(self):
    """ Get the spatial footprint as a polygonType object.
    """

    return self.Data.CatalogCoverage.SpatialCoverage.Polygon


def create_dpd_she_validated_shear_estimates(filename="None",
                                             spatial_footprint=None):
    """
        @TODO fill in docstring
    """

    dpd_she_validated_shear_estimates = read_xml_product(
        find_aux_file(sample_file_name), allow_pickled=False)

    # Overwrite the header with a new one to update the creation date (among
    # other things)
    dpd_she_validated_shear_estimates.Header = HeaderProvider.create_generic_header("SHE")

    __set_filename(dpd_she_validated_shear_estimates, filename)
    if spatial_footprint is not None:
        __set_spatial_footprint(dpd_she_validated_shear_estimates, spatial_footprint)

    return dpd_she_validated_shear_estimates


# Add a useful alias
create_validated_shear_estimates_product = create_dpd_she_validated_shear_estimates
