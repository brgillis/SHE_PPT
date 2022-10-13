""" @file phz_pf_output_catalog.py

    Created 17 Nov 2017

    Functions to create and output a detections data product.

    Origin: OU-PHZ - PfOutputCatalog (TODO: Confirm) in their data model
"""

__updated__ = "2021-11-18"

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

from ST_DataModelBindings.dpd.phz.raw.outputcatalog_stub import dpdPhzPfOutputCatalog
from ..product_utility import init_method_files, create_photoz_product_from_template


def init():
    """Adds some extra functionality to this product, with functions to get filenames."""

    init_method_files(binding_class=dpdPhzPfOutputCatalog, init_function=create_dpd_photoz_catalog)


def create_dpd_photoz_catalog(
    photoz_filename=None, gal_sed_filename=None, star_sed_filename=None, spatial_footprint=None
):
    """Creates a product of this type."""
    return create_photoz_product_from_template(
        photoz_filename=photoz_filename,
        gal_sed_filename=gal_sed_filename,
        star_sed_filename=star_sed_filename,
        spatial_footprint=spatial_footprint,
    )


# Add useful aliases
create_detections_product = create_dpd_photoz_catalog
create_dpd_phz_pf_output_catalog = create_dpd_photoz_catalog
create_phz_pf_output_catalog_product = create_dpd_photoz_catalog
