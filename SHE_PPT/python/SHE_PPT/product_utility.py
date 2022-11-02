""" @file product_utility.py

    Created 15 October 2020

    Utility functions related to data products
"""

__updated__ = "2021-08-19"

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

from enum import Enum
from typing import Optional

import ST_DM_DmUtils.DmUtils as dm_utils
import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider
from SHE_PPT.constants.classes import ShearEstimationMethods
from SHE_PPT.file_io import read_xml_product
from ST_DataModelBindings.bas.imp.raw.stc_stub import polygonType
from ST_DataModelBindings.dpd.she.intermediategeneral_stub import dpdSheIntermediateGeneral
from ST_DataModelBindings.dpd.she.intermediateobservationcatalog_stub import dpdSheIntermediateObservationCatalog
from ST_DataModelBindings.dpd.she.placeholdergeneral_stub import dpdShePlaceholderGeneral
from ST_DataModelBindings.pro import she_stub as she_pro
import ST_DataModelBindings.bas.cot_stub as cot_dict
import ST_DataModelBindings.bas.imp.stc_stub as stc_dict
import ST_DataModelBindings.bas.dtd_stub as dtd_dict
import ST_DataModelBindings.sys.dss_stub as dss_dict

from .constants.misc import DATA_SUBDIR
from .file_io import find_aux_file
from .logging import getLogger
from .utility import get_nested_attr

logger = getLogger(__name__)

FILENAME_INCLUDE_DATA_SUBDIR = False

LEN_DATA_SUBDIR = len(DATA_SUBDIR)


def coerce_include_data_subdir(filename: Optional[str]) -> Optional[str]:
    """Coerces a filename to always start with the data subdir."""

    if filename is None:
        return None
    if filename == "":
        return ""

    if (len(filename) < len(DATA_SUBDIR) or filename[:LEN_DATA_SUBDIR] != DATA_SUBDIR) and (
        len(filename) == 0 or filename[0] != "/"
    ):
        return DATA_SUBDIR + filename
    return filename


def coerce_no_include_data_subdir(filename: Optional[str]) -> Optional[str]:
    """Coerces a filename to not start with the data subdir."""

    if filename is None:
        return None
    if filename == "" or filename == "data/":
        return ""

    if len(filename) > len(DATA_SUBDIR) and filename[:LEN_DATA_SUBDIR] == DATA_SUBDIR:
        return filename[LEN_DATA_SUBDIR:]
    return filename


# Enum for names of placeholder and intermediate products
class ProductName(Enum):
    PLC_GENERAL = "DpdShePlaceholderGeneral"
    PLC_CAT = "DpdShePlaceholderCatalog"
    PLC_OBS_CAT = "DpdShePlaceholderObservationCatalog"
    PLC_TILE_CAT = "DpdShePlaceholderTileCatalog"
    INT_GENERAL = "DpdSheIntermediateGeneral"
    INT_CAT = "DpdSheIntermediateCatalog"
    INT_OBS_CAT = "DpdSheIntermediateObservationCatalog"
    INT_TILE_CAT = "DpdSheIntermediateTileCatalog"


# Dict to store the fits table versions for each shear estimation method
D_METHOD_FITS_VERSIONS = {
    ShearEstimationMethods.KSB: "8.0",
    ShearEstimationMethods.LENSMC: "8.0.1",
    ShearEstimationMethods.MOMENTSML: "8.0",
    ShearEstimationMethods.REGAUSS: "8.0",
}


# Enum for names of placeholder and intermediate products
def get_data_filename_from_product(p, attr_name=None):
    """Helper function to get a data filename from a product, adjusting for whether to include the data subdir
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

    return coerce_include_data_subdir(data_filename)


def set_data_filename_of_product(p, data_filename, attr_name=None):
    """Helper function to set a data filename of a product, adjusting for whether to include the
    data subdir as desired.
    """

    if data_filename is not None and len(data_filename) > 0 and data_filename[0] != "/":
        if FILENAME_INCLUDE_DATA_SUBDIR:
            data_filename = coerce_include_data_subdir(data_filename)

        else:
            data_filename = coerce_no_include_data_subdir(data_filename)

    if attr_name is None or attr_name == 0:
        p.Data.DataContainer.FileName = data_filename
    elif attr_name == -1:
        p.Data.FileName = data_filename
    else:
        get_nested_attr(p.Data, attr_name).DataContainer.FileName = data_filename


# Special functions we want to add to multiple products


def _set_spatial_footprint(self, p):
    """Set the spatial footprint. p can be either the spatial footprint, or
    another product which has a spatial footprint defined.
    """

    # Figure out where the spatial footprint is stored for this object
    target_attr = None
    if hasattr(self.Data, "SpatialCoverage"):
        target_attr = self.Data.SpatialCoverage
    elif hasattr(self.Data, "CatalogCoverage"):
        target_attr = self.Data.CatalogCoverage.SpatialCoverage

    if not target_attr:
        raise TypeError(
            f"Product {self} of type {type(self)} has no SpatialCoverage or CatalogCoverage attribute, "
            f"and so has no spatial footprint to be set with set_spatial_footprint."
        )

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
    elif hasattr(p, "Data") and hasattr(p.Data, "ImgSpatialFootprint"):
        poly = p.Data.ImgSpatialFootprint.Polygon
    elif hasattr(p, "Data") and hasattr(p.Data, "CatalogCoverage"):
        poly = p.Data.CatalogCoverage.SpatialCoverage.Polygon
    else:
        raise TypeError(
            "For set_spatial_footprint, must be provided a spatial footprint, a product which has it, "
            + "or the path to such a product. Received: "
            + str(type(p))
        )

    target_attr.Polygon = poly


def _get_spatial_footprint(self):
    """Get the spatial footprint as a polygonType object."""

    if not hasattr(self.Data, "CatalogCoverage"):
        raise TypeError(
            f"Product {self} of type {type(self)} has CatalogCoverage attribute, and so has no "
            f"spatial footprint to be retrieved with get_spatial_footprint."
        )

    return self.Data.CatalogCoverage.SpatialCoverage.Polygon


# Some of the most common versions of filename getters and setters for easy reuse


def set_filename_datastorage(self, filename):
    set_data_filename_of_product(self, filename, "DataStorage")


def get_filename_datastorage(self):
    return get_data_filename_from_product(self, "DataStorage")


def get_all_filenames_none(self):
    return []


def get_all_filenames_just_data(self):
    return [
        self.get_data_filename(),
    ]


def get_all_filenames_methods(self):
    all_filenames = [
        self.get_KSB_filename(),
        self.get_LensMC_filename(),
        self.get_MomentsML_filename(),
        self.get_REGAUSS_filename(),
    ]

    return all_filenames


def init_binding_class(
    binding_class,
    init_function=None,
):
    """Boilerplate code for initing any class."""

    if not hasattr(binding_class, "initialised"):
        binding_class.initialised = True
    else:
        return False

    # Add special methods in case they're needed
    binding_class.set_spatial_footprint = _set_spatial_footprint
    binding_class.get_spatial_footprint = _get_spatial_footprint

    # Use a lambda function to create a bound version of the init function
    binding_class.init_product = lambda self, *args, **kwargs: init_function(*args, **kwargs)

    return True


def init_no_files(
    binding_class,
    init_function=None,
):
    """Adds some extra functionality to a product, assuming it doesn't point to any files."""

    if not init_binding_class(binding_class, init_function):
        return

    # Add the data file name methods

    binding_class.get_all_filenames = get_all_filenames_none

    binding_class.has_files = False


def init_just_datastorage(
    binding_class,
    init_function=None,
):
    """Adds some extra functionality to a product, assuming it only only points to one file, in the data storage
    attribute.
    """

    if not init_binding_class(binding_class, init_function):
        return

    # Add the data file name methods

    binding_class.set_filename = set_filename_datastorage
    binding_class.get_filename = get_filename_datastorage

    binding_class.set_data_filename = set_filename_datastorage
    binding_class.get_data_filename = get_filename_datastorage

    binding_class.get_all_filenames = get_all_filenames_just_data

    binding_class.has_files = True


def init_method_files(
    binding_class,
    init_function=None,
):
    """Adds some extra functionality to a product, assuming it points to one file per shear estimation method
    in standard locations.
    """

    if not init_binding_class(binding_class, init_function):
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
            if not (
                filename is None
                or filename == "None"
                or filename == "data/None"
                or filename == ""
                or filename == "data/"
            ):
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


def _init_general_binding_class(binding_class):
    """Performs initialization for a general binding class, including setting up a dict of init functions."""

    if not hasattr(binding_class, "initialised"):
        binding_class.d_init_functions = {}
        binding_class.initialised = True
        return True
    else:
        return False


def init_intermediate_general(
    product_type_name=None,
    init_function=None,
):
    binding_class = dpdSheIntermediateGeneral

    first_init = _init_general_binding_class(binding_class=binding_class)

    # Set the init_function in the dict even if already inited
    if product_type_name:
        binding_class.d_init_functions[product_type_name] = init_function

    if not first_init:
        return

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


def init_int_obs_cat(
    product_type_name=None,
    init_function=None,
):
    binding_class = dpdSheIntermediateObservationCatalog

    first_init = _init_general_binding_class(binding_class=binding_class)

    # Set the init_function in the dict even if already inited
    if product_type_name:
        binding_class.d_init_functions[product_type_name] = init_function

    if not first_init:
        return

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


def init_placeholder_general(
    product_type_name=None,
    init_function=None,
):
    binding_class = dpdShePlaceholderGeneral

    first_init = _init_general_binding_class(binding_class=binding_class)

    # Set the init_function in the dict even if already inited
    if product_type_name:
        binding_class.d_init_functions[product_type_name] = init_function

    if not first_init:
        return

    # Add the data file name methods

    binding_class.set_filename = _set_plc_gen_data_filename
    binding_class.get_filename = _get_plc_gen_data_filename

    binding_class.set_data_filename = _set_plc_gen_data_filename
    binding_class.get_data_filename = _get_plc_gen_data_filename

    binding_class.get_all_filenames = _get_all_plc_gen_filenames

    binding_class.has_files = True


def create_product_from_template(
    template_filename, product_type_name, filename=None, data_filename=None, spatial_footprint=None
):
    """Generic function to create a data product object, using a template file as a base."""

    # Check input validity
    if filename and data_filename:
        raise ValueError("Only one of filename and data_filename should be provided to create_product_from_template.")
    if filename:
        data_filename = filename

    # Create the product
    p = read_xml_product(find_aux_file(template_filename))
    p.Header = HeaderProvider.create_generic_header(product_type_name)

    # Set the data_filename and spatial footprint
    if data_filename:
        p.set_data_filename(data_filename)
    if spatial_footprint:
        p.set_spatial_footprint(spatial_footprint)

    return p


def create_measurements_product_from_template(
    template_filename,
    product_type_name,
    KSB_filename=None,
    LensMC_filename=None,
    MomentsML_filename=None,
    REGAUSS_filename=None,
    spatial_footprint=None,
):
    """Function to create a data product object, using a template file as a base, specialized for shear measurements
    products.
    """

    p = create_product_from_template(
        template_filename=template_filename, product_type_name=product_type_name, spatial_footprint=spatial_footprint
    )

    p.set_KSB_filename(KSB_filename)
    p.set_LensMC_filename(LensMC_filename)
    p.set_MomentsML_filename(MomentsML_filename)
    p.set_REGAUSS_filename(REGAUSS_filename)

    return p


def create_catalog_coverage():
    SpatialCoverage = cot_dict.spatialFootprint()
    SpatialCoverage.Polygon = stc_dict.polygonType()
    SpatialCoverage.Polygon.Vertex.append(stc_dict.vertexType())
    vertex = SpatialCoverage.Polygon.Vertex[0]
    vertex.Position = dtd_dict.double2Type(C1=0, C2=0)

    return SpatialCoverage

def create_general_product_from_template(
    template_filename: str,
    product_type_name: str,
    general_product_type_name: str,
    filename: str = None,
):
    """Function to create a data product object, using a template file as a base, specialized for shear measurements
    products.
    """

    p = create_product_from_template(
        template_filename=template_filename, product_type_name=general_product_type_name, filename=filename
    )

    # Set the data we don't need to empty
    p.Data.IntData = []
    p.Data.FloatData = []

    # Label the type in the StringData
    p.Data.StringData = [f"TYPE:{product_type_name}"]

    return p


def get_method_cc_name(method: ShearEstimationMethods):
    """Get a Shear Estimation Method's name in both types of camel case."""

    method_lower = method.value.lower()

    # Get the camelCase version of the method name
    if method == ShearEstimationMethods.LENSMC:
        method_cc = "lensMc"
        method_caps = "LensMc"
    elif method == ShearEstimationMethods.MOMENTSML:
        method_cc = "momentsMl"
        method_caps = "MomentsMl"
    else:
        method_cc = method_lower
        method_caps = method_lower.capitalize()

    return method_cc, method_caps


def create_method_filestorage(
    method: ShearEstimationMethods,
    filename: Optional[str] = None,
):
    """Create a file storage object for a given shear estimates method."""

    method_cc, method_caps = get_method_cc_name(method)
    

    # Initialize the object
    shear_estimates = getattr(she_pro, f"she{method_caps}Measurements")()

    shear_estimates.DataStorage = dm_utils.create_fits_storage(
        getattr(she_pro, f"she{method_caps}MeasurementsFile"),
        filename,
        f"she.{method_cc}Measurements",
        version=D_METHOD_FITS_VERSIONS[method],
    )
    shear_estimates.Valid = "VALID"

    return shear_estimates


# Functions to set or get filenames for specific shear estimation methods
def set_method_filename(self, method: ShearEstimationMethods, filename: Optional[str] = None):

    _, method_caps = get_method_cc_name(method)
    method_attr = f"{method_caps}ShearMeasurements"
    data_attr = f"{method_attr}.DataStorage"


    if filename is None:
        if hasattr(self.Data, method_attr):
            setattr(self.Data, method_attr, None)
    else:
        if not hasattr(self.Data, method_attr) or getattr(self.Data, method_attr) is None:
            setattr(self.Data, method_attr, create_method_filestorage(method, filename))
        set_data_filename_of_product(self, filename, data_attr)


def get_method_filename(self, method: ShearEstimationMethods):

    _, method_caps = get_method_cc_name(method)
    method_attr = f"{method_caps}ShearMeasurements"
    data_attr = f"{method_attr}.DataStorage"


    if not hasattr(self.Data, method_attr) or getattr(self.Data, method_attr) is None:
        return None

    return get_data_filename_from_product(self, data_attr)


def set_KSB_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, ShearEstimationMethods.KSB, filename)


def set_LensMC_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, ShearEstimationMethods.LENSMC, filename)


def set_MomentsML_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, ShearEstimationMethods.MOMENTSML, filename)


def set_REGAUSS_filename(self, filename: Optional[str] = None):
    return set_method_filename(self, ShearEstimationMethods.REGAUSS, filename)


def get_KSB_filename(self):
    return get_method_filename(self, ShearEstimationMethods.KSB)


def get_LensMC_filename(self):
    return get_method_filename(self, ShearEstimationMethods.LENSMC)


def get_MomentsML_filename(self):
    return get_method_filename(self, ShearEstimationMethods.MOMENTSML)


def get_REGAUSS_filename(self):
    return get_method_filename(self, ShearEstimationMethods.REGAUSS)

def create_data_container(file_name, file_status="PROPOSED"):
    """Creates a data container binding.

    Parameters
    ----------
    file_name: str
        The data file name.
    file_status: str, optional
        The status of the file: PROPOSED, PROCESSING, COMMITTED, VALIDATED,
        ARCHIVED or DELETED. Default is PROPOSED.

    Returns:
    --------
    object
        The data container binding.

    """
    # Create the data container binding
    data_container = dss_dict.dataContainer()

    # Fill it with the given values
    data_container.FileName = file_name
    data_container.filestatus = file_status

    return data_container

def create_fits_storage(binding_class, file_name, file_format, version):
    """Creates a fits file storage binding.

    Parameters
    ----------
    binding_class: class
        The fits file binding class.
    file_name: str
        The fits file name.
    file_format: str
        The fits file format.
    version: str
        The fits file format version.

    Returns
    -------
    object
        The fits file storage binding.

    """
    # Create the appropriate fits file storage binding
    storage = binding_class.Factory()

    # Fill it with the given values
    storage.format = file_format
    if version!="":
        storage.version = version
    storage.DataContainer = create_data_container(file_name)

    return storage

