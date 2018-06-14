""" @file detections.py

    Created 22 Aug 2017

    Format definition for detections table.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from collections import OrderedDict

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import hash_any
from astropy.table import Table


logger = getLogger(mv.logger_name)

class DetectionsTableMeta(object):
    """
        @brief A class defining the metadata for detections tables.
    """

    def __init__(self):

        self.__version__ = "0.1"
        self.table_format = "mer.finalCatalog"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                   ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())

class DetectionsTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the detections_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = DetectionsTableMeta()

        # And a quick alias for it
        self.m = self.meta

        # Get the version from the meta class
        self.__version__ = self.m.__version__

        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all

        # Dicts for less-used properties
        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        def set_column_properties(name, is_optional = False, comment = None, dtype = ">f4", fits_dtype = "E",
                                   length = 1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Column names and info

        self.ID = set_column_properties("ObjectId", dtype = ">i8", fits_dtype = "K")
        
        self.seg_ID = set_column_properties("SEGMENTATION_MAP_ID", is_optional=True, dtype = ">i4", fits_dtype="j")

        self.gal_x_world = set_column_properties("RightAscension", is_optional = False, comment = "deg")
        self.gal_y_world = set_column_properties("Declination", is_optional = False, comment = "deg")

        self.FluxGextDECamAper = set_column_properties("FluxGextDECamAper", is_optional = True, comment = None)
        self.FluxRextDECamAper = set_column_properties("FluxRextDECamAper", is_optional = True, comment = None)
        self.FluxIextDECamAper = set_column_properties("FluxIextDECamAper", is_optional = True, comment = None)
        self.FluxZextDECamAper = set_column_properties("FluxZextDECamAper", is_optional = True, comment = None)
        self.FluxYextDECamAper = set_column_properties("FluxYextDECamAper", is_optional = True, comment = None)

        self.FluxUextOmegaCAMAper = set_column_properties("FluxUextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxGextOmegaCAMAper = set_column_properties("FluxGextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxRextOmegaCAMAper = set_column_properties("FluxRextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxIextOmegaCAMAper = set_column_properties("FluxIextOmegaCAMAper", is_optional = True, comment = None)

        self.FluxVISAper = set_column_properties("FluxVISAper", is_optional = True, comment = None)
        self.FluxYAper = set_column_properties("FluxYAper", is_optional = True, comment = None)
        self.FluxJAper = set_column_properties("FluxJAper", is_optional = True, comment = None)
        self.FluxHAper = set_column_properties("FluxHAper", is_optional = True, comment = None)

        self.FluxerrGextDECamAper = set_column_properties("FluxerrGextDECamAper", is_optional = True, comment = None)
        self.FluxerrRextDECamAper = set_column_properties("FluxerrRextDECamAper", is_optional = True, comment = None)
        self.FluxerrIextDECamAper = set_column_properties("FluxerrIextDECamAper", is_optional = True, comment = None)
        self.FluxerrZextDECamAper = set_column_properties("FluxerrZextDECamAper", is_optional = True, comment = None)
        self.FluxerrYextDECamAper = set_column_properties("FluxerrYextDECamAper", is_optional = True, comment = None)

        self.FluxerrUextOmegaCAMAper = set_column_properties("FluxerrUextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxerrGextOmegaCAMAper = set_column_properties("FluxerrGextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxerrRextOmegaCAMAper = set_column_properties("FluxerrRextOmegaCAMAper", is_optional = True, comment = None)
        self.FluxerrIextOmegaCAMAper = set_column_properties("FluxerrIextOmegaCAMAper", is_optional = True, comment = None)

        self.FluxerrVISAper = set_column_properties("FluxerrVISAper", is_optional = True, comment = None)
        self.FluxerrYAper = set_column_properties("FluxerrYAper", is_optional = True, comment = None)
        self.FluxerrJAper = set_column_properties("FluxerrJAper", is_optional = True, comment = None)
        self.FluxerrHAper = set_column_properties("FluxerrHAper", is_optional = True, comment = None)

        self.FluxGextDECamTphot = set_column_properties("FluxGextDECamTphot", is_optional = True, comment = None)
        self.FluxRextDECamTphot = set_column_properties("FluxRextDECamTphot", is_optional = True, comment = None)
        self.FluxIextDECamTphot = set_column_properties("FluxIextDECamTphot", is_optional = True, comment = None)
        self.FluxZextDECamTphot = set_column_properties("FluxZextDECamTphot", is_optional = True, comment = None)
        self.FluxYextDECamTphot = set_column_properties("FluxYextDECamTphot", is_optional = True, comment = None)

        self.FluxUextOmegaCAMTphot = set_column_properties("FluxUextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxGextOmegaCAMTphot = set_column_properties("FluxGextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxRextOmegaCAMTphot = set_column_properties("FluxRextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxIextOmegaCAMTphot = set_column_properties("FluxIextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxerrGextDECamTphot = set_column_properties("FluxerrGextDECamTphot", is_optional = True, comment = None)
        self.FluxerrRextDECamTphot = set_column_properties("FluxerrRextDECamTphot", is_optional = True, comment = None)
        self.FluxerrIextDECamTphot = set_column_properties("FluxerrIextDECamTphot", is_optional = True, comment = None)
        self.FluxerrZextDECamTphot = set_column_properties("FluxerrZextDECamTphot", is_optional = True, comment = None)
        self.FluxerrYextDECamTphot = set_column_properties("FluxerrYextDECamTphot", is_optional = True, comment = None)

        self.FluxerrUextOmegaCAMTphot = set_column_properties("FluxerrUextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxerrGextOmegaCAMTphot = set_column_properties("FluxerrGextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxerrRextOmegaCAMTphot = set_column_properties("FluxerrRextOmegaCAMTphot", is_optional = True, comment = None)
        self.FluxerrIextOmegaCAMTphot = set_column_properties("FluxerrIextOmegaCAMTphot", is_optional = True, comment = None)

        self.FlagGextDECam = set_column_properties("FlagGextDECam", is_optional = True, comment = None)
        self.FlagRextDECam = set_column_properties("FlagRextDECam", is_optional = True, comment = None)
        self.FlagIextDECam = set_column_properties("FlagIextDECam", is_optional = True, comment = None)
        self.FlagZextDECam = set_column_properties("FlagZextDECam", is_optional = True, comment = None)
        self.FlagYextDECam = set_column_properties("FlagYextDECam", is_optional = True, comment = None)

        self.FlagUextOmegaCAM = set_column_properties("FlagUextOmegaCAM", is_optional = True, comment = None)
        self.FlagGextOmegaCAM = set_column_properties("FlagGextOmegaCAM", is_optional = True, comment = None)
        self.FlagRextOmegaCAM = set_column_properties("FlagRextOmegaCAM", is_optional = True, comment = None)
        self.FlagIextOmegaCAM = set_column_properties("FlagIextOmegaCAM", is_optional = True, comment = None)

        self.FlagVIS = set_column_properties("FlagVIS ", is_optional = True, comment = None)
        self.FlagY = set_column_properties("FlagY   ", is_optional = True, comment = None)
        self.FlagJ = set_column_properties("FlagJ   ", is_optional = True, comment = None)
        self.FlagH = set_column_properties("FlagH   ", is_optional = True, comment = None)

        self.DeblendingFlag = set_column_properties("DeblendingFlag", is_optional = True, comment = None)
        self.StarFlag = set_column_properties("StarFlag", is_optional = True, comment = None)

        self.MuMax = set_column_properties("MuMax   ", is_optional = True, comment = None)

        self.Isoarea = set_column_properties("Isoarea ", is_optional = True, comment = None)

        self.PositionAngle = set_column_properties("PositionAngle", is_optional = True, comment = None)

        self.Ellipticity = set_column_properties("Ellipticity", is_optional = True, comment = None)
        
        self.MagStarGal = set_column_properties("MAG_STARGAL_SEP", is_optional=True, comment = None)


        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported
detections_table_format = DetectionsTableFormat()

# And a convient alias for it
tf = detections_table_format


def make_detections_table_header(model_hash = None,
                                 model_seed = None,
                                 noise_seed = None):
    """
        @brief Generate a header for a detections table.

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    return header

def initialise_detections_table(image_group_phl = None,
                                options = None,
                                optional_columns = None,
                                model_hash = None,
                                model_seed = None,
                                noise_seed = None):
    """
        @brief Initialise a detections table.

        @param image_group_phl <SHE_SIM.ImageGroup>

        @param options <dict> Options dictionary

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is none

        @param detector <int?> Detector for this image, if applicable. Will override ID of image object if set

        @param obs_time <str> Mean observation time of the corresponding detections

        @return detections_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    names = []
    init_cols = []
    dtypes = []
    for colname in tf.all:
        if (colname in tf.all_required) or (colname in optional_columns):
            names.append(colname)
            init_cols.append([])
            dtypes.append((tf.dtypes[colname], tf.lengths[colname]))

    detections_table = Table(init_cols, names = names,
                             dtype = dtypes)

    if image_group_phl is not None:

        # Get values from the image object, unless they were passed explicitly

        if model_seed is None:
            model_seed = image_group_phl.get_seed()

    if options is not None:

        # Get values from the options dict, unless they were passed explicitly

        if model_hash is None:
            model_hash = hash_any(options.items(), format = "base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']

    detections_table.meta = make_detections_table_header(model_hash = model_hash,
                                                         model_seed = model_seed,
                                                         noise_seed = noise_seed)

    assert(is_in_format(detections_table, tf))

    return detections_table
