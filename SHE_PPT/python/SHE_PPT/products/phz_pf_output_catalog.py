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
import ST_DataModelBindings.dpd.phz.outputcatalog_stub as phz_dpd_output
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
import ST_DataModelBindings.bas.cat_stub as cat_dict
import ST_DataModelBindings.pro.phz_stub as phz_dict


from ..product_utility import (init_method_files, create_catalog_coverage, 
                               create_data_container, create_fits_storage)


def init():
    """Adds some extra functionality to this product, with functions to get filenames."""

    init_method_files(binding_class=dpdPhzPfOutputCatalog, init_function=create_dpd_photoz_catalog)


def create_dpd_photoz_catalog(photoz_filename = None,  star_sed_filename = None, galaxy_sed_filename = None, spatial_footprint = None ):
    """Creates the PHZ output catalog bindings.

    Inputs
    ------
    photo_Z_file
        The name of the photo_z file to be wrapped in the binding.
    star_sed_file
        The name of the star_sed file to be wrapped in the binding. Can be ""
    Galaxy_sed_file
        The name of the galaxy_sed file to be wrapped in the binding. Can be ""
    spatialFootprint
        The coverage of the input catalog
    TileIndex
        the index of the MER tile
    Returns
    -------
    object
        The PHZ output catalog bindings.

    """
    version = "0.9"
    spatial_footprint = create_catalog_coverage()
    tile_index = 0

    # Create the appropriate data product binding
    dpd = phz_dpd_output.DpdPhzPfOutputCatalog()
    
    # Add the generic header to the data product
    dpd.Header = HeaderProvider.create_generic_header('DpdPhzPfOutputCatalog')

    dpd.Data = phz_dict.phzPfOutputCatalog.Factory()

    # Add the catalog id
    dpd.Data.IdCatalog = 0

    # Add the coverage
    dpd.Data.SpatialCoverage = spatial_footprint
    dpd.Data.TileIndex = tile_index




    # Add the catalog descriptions
    # NOTE: We have multiple catalogs, but conceptually they are part of a single one,
    #       partitioned by columns. However, the XSD only let us define one (and only one)
    #       PathToCatalogDefinition. MER situation is similar (they have final and cutout catalogs),
    #       and they do the same.

    description = cat_dict.catalogDescription()

    description.PathToCatalogFile = "Data.PhzCatalog.DataContainer.FileName"
    description.CatalogType = "NOT_PROXY"
    description.CatalogOrigin = "MEASURED_WIDE"
    description.CatalogOrigin = "MEASURED_WIDE"
    description.CatalogName = "Phz-PhotoZ-Catalog"
    description.CatalogFormatHDU = 1


    dpd.Data.CatalogDescription.append(description)

    # Add the files
    
    dpd.Data.PhzCatalog = create_fits_storage(
        phz_dict.phzPhotoZCatalog,
        photoz_filename,
        "phz.photoZCatalog",
        version)

    if star_sed_filename!="":
        dpd.Data.StarSedCatalog = create_fits_storage(
            phz_dict.phzStarSedCatalog,
            star_sed_filename,
            "phz.sedCatalog",
            version)

    if galaxy_sed_filename!="":
        dpd.Data.GalaxySedCatalog = create_fits_storage(
            phz_dict.phzGalaxySedCatalog,
            galaxy_sed_filename,
            "phz.sedCatalog",
            version)
    
    if spatial_footprint:
        dpd.set_spatial_footprint(spatial_footprint)
    return dpd

# Add useful aliases
create_detections_product = create_dpd_photoz_catalog
create_dpd_phz_pf_output_catalog = create_dpd_photoz_catalog
create_phz_pf_output_catalog_product = create_dpd_photoz_catalog
