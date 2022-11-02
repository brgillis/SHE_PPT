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

from typing import Optional

from ST_DataModelBindings.dpd.phz.raw.outputcatalog_stub import dpdPhzPfOutputCatalog
import ST_DataModelBindings.dpd.phz.outputcatalog_stub as phz_dpd_output
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
import ST_DataModelBindings.bas.cat_stub as cat_dict
import ST_DataModelBindings.pro.phz_stub as phz_dict
from SHE_PPT.constants.classes import PhotozCatalogMethods
import ST_DM_DmUtils.DmUtils as dm_utils


from ..product_utility import (init_binding_class, create_fits_storage,
                               set_data_filename_of_product, get_data_filename_from_product)



def init():
    """
        Adds some extra functionality to the dpdPhzPfOutputCatalog product
    """

    binding_class = dpdPhzPfOutputCatalog

    if not init_binding_class(binding_class,
                              init_function=create_dpd_photoz_catalog):
        return

    # Add the data file name methods

    binding_class.set_photoz_filename = set_photoz_filename
    binding_class.get_photoz_filename = get_photoz_filename

    binding_class.set_gal_sed_filename = set_gal_sed_filename
    binding_class.get_gal_sed_filename = get_gal_sed_filename

    binding_class.set_star_sed_filename = set_star_sed_filename
    binding_class.get_star_sed_filename = get_star_sed_filename

    binding_class.get_all_filenames = get_all_filenames

    binding_class.get_method_filename = get_method_filename
    binding_class.set_method_filename = set_method_filename

    binding_class.has_files = True



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
    
    dpd.Data.SpatialCoverage = dm_utils.create_spatial_footprint()
    if spatial_footprint:
        dpd.Data.SpatialCoverage = spatial_footprint
    return dpd


def set_method_filename(self, method, filename = None):
   
    method_caps = method.value
    if method_caps.startswith("PhotoZ"):
        method_caps = "PhzCatalog"
    method_attr = f"{method_caps}"
    data_attr = f"{method_attr}"

    if filename is None:
        if hasattr(self.Data, method_attr):
            setattr(self.Data, method_attr, None)
    else:
        if not hasattr(self.Data, method_attr) or getattr(self.Data, method_attr) is None:
            setattr(self.Data, method_attr, create_method_filestorage(method, filename))
        set_data_filename_of_product(self, filename, data_attr)

def get_method_filename(self, method: PhotozCatalogMethods):
    
    method_caps = method.value
    if method_caps.startswith("PhotoZ"):
        method_caps = "PhzCatalog"
    method_attr = f"{method_caps}"
    data_attr = f"{method_attr}"

    if not hasattr(self.Data, method_attr) or getattr(self.Data, method_attr) is None:
        return None

    return get_data_filename_from_product(self, data_attr)


def get_all_filenames(self):
        
    all_filenames = [self.get_photoz_filename(), 
                     self.get_gal_sed_filename(), 
                     self.get_star_sed_filename()]
    
    return all_filenames

def create_method_filestorage(
    method: PhotozCatalogMethods,
    filename: Optional[str] = None,
):
    """Create a file storage object for a given shear estimates method."""

    method_cc, method_caps = get_method_cc_name(method)
    method_val = method.value
    version = "0.9"
    if "sed" in method_val.lower():
        format = "sedCatalog"
    elif "photoz" in method_val.lower():
        format = "photoZCatalog"

    phz_catalog = getattr(phz_pro, f"phz{method_val}")()
    phz_catalog.DataStorage = dm_utils.create_fits_storage(
        getattr(phz_pro, f"phz{method_val}"), filename, f"phz.{format}", version
    )
    phz_catalog.Valid = "VALID"
    return phz_catalog
    
def set_photoz_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, PhotozCatalogMethods.PHOTOZ, filename)


def set_gal_sed_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, PhotozCatalogMethods.GALSED, filename)


def set_star_sed_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, PhotozCatalogMethods.STARSED, filename)


def get_photoz_filename(self):
    return get_method_filename(self, PhotozCatalogMethods.PHOTOZ)


def get_gal_sed_filename(self):
    return get_method_filename(self, PhotozCatalogMethods.GALSED)


def get_star_sed_filename(self):
    return get_method_filename(self, PhotozCatalogMethods.STARSED)