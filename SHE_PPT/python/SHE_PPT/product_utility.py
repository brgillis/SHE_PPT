""" @file product_utility.py

    Created 15 October 2020

    Utility functions related to data products
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

from EL_PythonUtils.utilities import run_only_once

from SHE_PPT.file_io import read_xml_product
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.intermediategeneral_stub import dpdSheIntermediateGeneral
from ST_DataModelBindings.dpd.she.intermediateobservationcatalog_stub import dpdSheIntermediateObservationCatalog
from ST_DataModelBindings.dpd.she.placeholdergeneral_stub import dpdShePlaceholderGeneral

from .file_io import find_aux_file
from .logging import getLogger
from .utility import get_nested_attr


logger = getLogger(__name__)

filename_include_data_subdir = False
data_subdir = "data/"
len_data_subdir = len(data_subdir)


def get_data_filename_from_product(p, attr_name=None):
    """ Helper function to get a data filename from a product, adjusting for whether to include the data subdir
        as desired.
    """

    if attr_name is None or attr_name == 0:
        data_filename = p.Data.DataContainer.FileName
    elif attr_name == -1:
        data_filename = p.Data.FileName
    else:
        data_filename = get_nested_attr(p.Data, attr_name).DataContainer.FileName

    if data_filename is None:
        return None

    # Silently force the filename returned to start with "data/" regardless of
    # whether the returned value does, unless it's absolute
    if len(data_filename) > 0 and (data_filename[0:len_data_subdir] == data_subdir or data_filename[0] == "/"):
        return data_filename

    return data_subdir + data_filename


def set_data_filename_of_product(p, data_filename, attr_name=None):
    """ Helper function to set a data filename of a product, adjusting for whether to include the
        data subdir as desired.
    """

    if data_filename is not None and len(data_filename) > 0 and data_filename[0] != "/":
        if filename_include_data_subdir:

            # Silently force the filename returned to start with "data/" regardless of
            # whether the returned value does
            if data_filename[0:len_data_subdir] != data_subdir:
                data_filename = data_subdir + data_filename

        else:

            # Silently force the filename returned to NOT start with "data/"
            # regardless of whether the returned value does
            if data_filename[0:len_data_subdir] == data_subdir:
                data_filename = data_filename.replace(data_subdir, "", 1)

    if attr_name is None or attr_name == 0:
        p.Data.DataContainer.FileName = data_filename
    elif attr_name == -1:
        p.Data.FileName = data_filename
    else:
        get_nested_attr(p.Data, attr_name).DataContainer.FileName = data_filename

# Special functions we want to add to multiple products


def _set_spatial_footprint(self, p):
    """ Set the spatial footprint. p can be either the spatial footprint, or
        another product which has a spatial footprint defined.
    """

    if not hasattr(self.Data, "CatalogCoverage"):
        raise TypeError(f"Product {self} of type {type(self)} has CatalogCoverage attribute, and so has no "
                        f"spatial footprint to be set with set_spatial_footprint.")

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


def _get_spatial_footprint(self):
    """ Get the spatial footprint as a polygonType object.
    """

    if not hasattr(self.Data, "CatalogCoverage"):
        raise TypeError(f"Product {self} of type {type(self)} has CatalogCoverage attribute, and so has no "
                        f"spatial footprint to be retrieved with get_spatial_footprint.")

    return self.Data.CatalogCoverage.SpatialCoverage.Polygon

# Some of the most common versions of filename getters and setters for easy reuse


def set_filename_datastorage(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def get_filename_datastorage(self):
    return get_data_filename_from_product(self, "DataStorage")


def get_all_filenames_none(self):
    return []


def get_all_filenames_just_data(self):
    return [self.get_data_filename(), ]


def init_binding_class(binding_class):
    """ Boilerplate code for initing any class.
    """

    if not hasattr(binding_class, "initialised"):
        binding_class.initialised = True
    else:
        return False

    # Add special methods in case they're needed
    binding_class.set_spatial_footprint = _set_spatial_footprint
    binding_class.get_spatial_footprint = _get_spatial_footprint

    return True


def init_no_files(binding_class):
    """ Adds some extra functionality to a product, assuming it doesn't point to any files.
    """

    if not init_binding_class(binding_class):
        return

    # Add the data file name methods

    binding_class.get_all_filenames = get_all_filenames_none

    binding_class.has_files = False


def init_just_datastorage(binding_class):
    """ Adds some extra functionality to a product, assuming it only only points to one file, in the data storage
        attribute.
    """

    if not init_binding_class(binding_class):
        return

    # Add the data file name methods

    binding_class.set_filename = set_filename_datastorage
    binding_class.get_filename = get_filename_datastorage

    binding_class.set_data_filename = set_filename_datastorage
    binding_class.get_data_filename = get_filename_datastorage

    binding_class.get_all_filenames = get_all_filenames_just_data

    binding_class.has_files = True


def _set_int_gen_data_filename(self, filename, i=0):
    set_data_filename_of_product(self, filename, f"DataStorage[{i}]")


def _get_int_gen_data_filename(self, i=0):
    return get_data_filename_from_product(self, f"DataStorage[{i}]")


def _get_all_generic_filenames(self, method):

    all_filenames = []

    try:
        for i in range(len(self.Data.DataStorage)):
            # Catch issues with the range not matching the actual elements in the list and warn if caught
            filename = method(self, i)
            if not (filename is None or filename == "None" or filename == "data/None" or
                    filename == "" or filename == "data/"):
                all_filenames.append(filename)

        return all_filenames
    except TypeError as e:
        if "has no len()" not in str(e):
            raise
        # Only a single filename, so output that
        all_filenames.append(method(self))

    return all_filenames


def _get_all_int_gen_filenames(self):

    return _get_all_generic_filenames(self, _get_int_gen_data_filename)


@run_only_once
def init_intermediate_general():

    binding_class = dpdSheIntermediateGeneral

    # Add the data file name methods

    binding_class.set_filename = _set_int_gen_data_filename
    binding_class.get_filename = _get_int_gen_data_filename

    binding_class.set_data_filename = _set_int_gen_data_filename
    binding_class.get_data_filename = _get_int_gen_data_filename

    binding_class.get_all_filenames = _get_all_int_gen_filenames

    binding_class.has_files = True


def _set_int_obs_cat_data_filename(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def _get_int_obs_cat_data_filename(self):
    return get_data_filename_from_product(self, "DataStorage")


def _get_all_int_obs_cat_filenames(self):

    return _get_all_generic_filenames(self, _get_int_obs_cat_data_filename)


@run_only_once
def init_int_obs_cat():

    binding_class = dpdSheIntermediateObservationCatalog

    # Add the data file name methods

    binding_class.set_filename = _set_int_obs_cat_data_filename
    binding_class.get_filename = _get_int_obs_cat_data_filename

    binding_class.set_data_filename = _set_int_obs_cat_data_filename
    binding_class.get_data_filename = _get_int_obs_cat_data_filename

    binding_class.get_all_filenames = _get_all_int_obs_cat_filenames

    binding_class.has_files = True


def _set_plc_gen_data_filename(self, filename, i=0):
    set_data_filename_of_product(self, filename, f"DataStorage[{i}]")


def _get_plc_gen_data_filename(self, i=0):
    return get_data_filename_from_product(self, f"DataStorage[{i}]")


def _get_all_plc_gen_filenames(self):

    return _get_all_generic_filenames(self, _get_plc_gen_data_filename)


@run_only_once
def init_placeholder_general():

    binding_class = dpdShePlaceholderGeneral

    # Add the data file name methods

    binding_class.set_filename = _set_plc_gen_data_filename
    binding_class.get_filename = _get_plc_gen_data_filename

    binding_class.set_data_filename = _set_plc_gen_data_filename
    binding_class.get_data_filename = _get_plc_gen_data_filename

    binding_class.get_all_filenames = _get_all_plc_gen_filenames

    binding_class.has_files = True


def create_product_from_template(template_filename,
                                 product_name,
                                 filename=None,
                                 data_filename=None,
                                 spatial_footprint=None):
    """ Generic function to create a data product object, using a template file as a base.
    """

    # Check input validity
    if filename and data_filename:
        raise ValueError("Only one of filename and data_filename should be provided to create_product_from_template.")
    if filename:
        data_filename = filename

    # Create the product
    p = read_xml_product(find_aux_file(template_filename))
    p.Header = HeaderProvider.create_generic_header(product_name)

    # Set the data_filename and spatial footprint
    if data_filename:
        p.set_data_filename(data_filename)
    if spatial_footprint:
        p.set_spatial_footprint(spatial_footprint)

    return p


def create_measurements_product_from_template(template_filename,
                                              product_name,
                                              KSB_filename=None,
                                              LensMC_filename=None,
                                              MomentsML_filename=None,
                                              REGAUSS_filename=None,
                                              spatial_footprint=None):
    """ Function to create a data product object, using a template file as a base, specialized for shear measurements
        products.
    """

    p = create_product_from_template(template_filename=template_filename,
                                     product_name=product_name,
                                     spatial_footprint=spatial_footprint)

    p.set_KSB_filename(KSB_filename)
    p.set_LensMC_filename(LensMC_filename)
    p.set_MomentsML_filename(MomentsML_filename)
    p.set_REGAUSS_filename(REGAUSS_filename)

    return p
