""" @file she_reconciled_lensmc_chains.py

    Created 5 Oct 2020

    Functions to create and output a reconciled_lensmc_chains_data data product.

    Origin: OU-SHE
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

__updated__ = "2021-06-10"


import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.reconciledlensmcchains_stub import dpdSheReconciledLensMcChains

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product


sample_file_name = "SHE_PPT/sample_reconciled_lensmc_chains.xml"


def init():
    """
        Initialisers for Reconciled LensMC Chains
    """

    binding_class = dpdSheReconciledLensMcChains

    # Add the data file name methods

    binding_class.set_filename = _set_filename
    binding_class.get_filename = _get_filename
    binding_class.set_data_filename = _set_filename
    binding_class.get_data_filename = _get_filename

    binding_class.get_all_filenames = _get_all_filenames

    binding_class.get_spatial_footprint = _get_spatial_footprint
    binding_class.set_spatial_footprint = _set_spatial_footprint

    binding_class.has_files = False



def _set_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def _get_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def _get_all_filenames(self):

    all_filenames = [self.get_filename()]

    return all_filenames


def _set_spatial_footprint(self, p):
    """ Set the spatial footprint. p can be either the spatial footprint, or
        another product which has a spatial footprint defined.
    """

    # Figure out how the spatial footprint was passed to us
    if isinstance(p, str):
        # If we got a filepath, read it in and apply this function to the read-in product
        _set_spatial_footprint(self, read_xml_product(p))
        return
    if isinstance(p, polygonType):
        poly = p
    elif hasattr(p, "Polygon"):
        poly = p.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "SpatialCoverage"):
        poly = p.Data.SpatialCoverage.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "CatalogCoverage"):
        poly = p.Data.CatalogCoverage.SpatialCoverage.Polygon
    else:
        raise TypeError("For set_spatial_footprint, must be provided a spatial footprint, a product which has it, " +
                        "or the path to such a product. Received: " + str(type(p)))

    self.Data.SpatialCoverage.Polygon = poly

    return


def _get_spatial_footprint(self):
    """ Get the spatial footprint as a polygonType object.
    """

    return self.Data.CatalogCoverage.SpatialCoverage.Polygon


def create_dpd_she_reconciled_lensmc_chains(filename="None",
                                            spatial_footprint=None):
    """
        @TODO fill in docstring
    """

    dpd_she_reconciled_lensmc_chains = read_xml_product(find_aux_file(sample_file_name))

    dpd_she_reconciled_lensmc_chains.Header = HeaderProvider.create_generic_header("DpdSheReconciledLensMcChains")

    if filename:
        _set_filename(dpd_she_reconciled_lensmc_chains, filename)
    if spatial_footprint is not None:
        _set_spatial_footprint(dpd_she_reconciled_lensmc_chains, spatial_footprint)
    return dpd_she_reconciled_lensmc_chains


# Add a useful alias
create_reconciled_lensmc_chains_product = create_dpd_she_reconciled_lensmc_chains


def create_she_reconciled_lensmc_chains(filename="None"):
    """
        @TODO fill in docstring
    """

    she_reconciled_lensmc_chains = SheReconciledLensMcChains()

    she_reconciled_lensmc_chains.format = "she.lensMcChains"
    she_reconciled_lensmc_chains.version = "8.0"

    _set_filename(dpd_she_reconciled_lensmc_chains, filename)

    return she_reconciled_lensmc_chains
