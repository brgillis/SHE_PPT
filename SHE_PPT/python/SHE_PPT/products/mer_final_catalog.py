""" @file mer_final_catalog.py

    Created 17 Nov 2017

    Functions to create and output a detections data product.

    Origin: OU-MER - FinalCatalog (TODO: Confirm) in their data model
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

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.dpd.mer.raw.finalcatalog_stub import dpdMerFinalCatalog

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import init_just_datastorage


sample_file_name = "SHE_PPT/sample_mer_final_catalog.xml"


def init():
    """ Adds some extra functionality to this product, with functions to get filenames. """

    init_just_datastorage(binding_class=dpdMerFinalCatalog)


def create_dpd_she_detections(data_filename=None):
    """
        @TODO fill in docstring
    """

    dpd_she_detections = read_xml_product(
        find_aux_file(sample_file_name))

    dpd_she_detections.Header = HeaderProvider.create_generic_header("DpdMerFinalCatalog")

    if data_filename is not None:
        dpd_she_detections.set_data_filename(data_filename)

    return dpd_she_detections


# Add useful aliases
create_detections_product = create_dpd_she_detections
create_dpd_mer_final_catalog = create_dpd_she_detections
create_mer_final_catalog_product = create_dpd_she_detections
