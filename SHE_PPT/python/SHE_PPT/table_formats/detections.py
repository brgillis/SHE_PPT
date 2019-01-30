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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

from collections import OrderedDict

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

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Column names and info

        self.ID = set_column_properties("OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.seg_ID = set_column_properties("SEGMENTATION_MAP_ID", dtype=">i8", fits_dtype="K")

        self.gal_x_world = set_column_properties("RIGHT_ASCENSION", dtype=">f8",, is_optional=False, comment="deg")
        self.gal_y_world = set_column_properties("DECLINATION", dtype=">f8",, is_optional=False, comment="deg")

        self.MAG_G_EXT_DECAM_APER = set_column_properties("MAG_G_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAG_R_EXT_DECAM_APER = set_column_properties("MAG_R_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAG_I_EXT_DECAM_APER = set_column_properties("MAG_I_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAG_Z_EXT_DECAM_APER = set_column_properties("MAG_Z_EXT_DECAM_APER", is_optional=True, comment=None)

        self.MAG_U_EXT_OMEGACAM_APER = set_column_properties("MAG_U_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAG_G_EXT_OMEGACAM_APER = set_column_properties("MAG_G_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAG_R_EXT_OMEGACAM_APER = set_column_properties("MAG_R_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAG_I_EXT_OMEGACAM_APER = set_column_properties("MAG_I_EXT_OMEGACAM_APER", is_optional=True, comment=None)

        self.MAG_U_EXT_LSST_APER = set_column_properties("MAG_U_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAG_G_EXT_LSST_APER = set_column_properties("MAG_G_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAG_R_EXT_LSST_APER = set_column_properties("MAG_R_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAG_I_EXT_LSST_APER = set_column_properties("MAG_I_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAG_Z_EXT_LSST_APER = set_column_properties("MAG_Z_EXT_LSST_APER", is_optional=True, comment=None)

        self.MAG_VIS_APER = set_column_properties("MAG_VIS_APER", is_optional=True, comment=None)
        self.MAG_Y_APER = set_column_properties("MAG_Y_APER", is_optional=True, comment=None)
        self.MAG_J_APER = set_column_properties("MAG_J_APER", is_optional=True, comment=None)
        self.MAG_H_APER = set_column_properties("MAG_H_APER", is_optional=True, comment=None)

        self.MAGERR_G_EXT_DECAM_APER = set_column_properties("MAGERR_G_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAGERR_R_EXT_DECAM_APER = set_column_properties("MAGERR_R_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAGERR_I_EXT_DECAM_APER = set_column_properties("MAGERR_I_EXT_DECAM_APER", is_optional=True, comment=None)
        self.MAGERR_Z_EXT_DECAM_APER = set_column_properties("MAGERR_Z_EXT_DECAM_APER", is_optional=True, comment=None)

        self.MAGERR_U_EXT_OMEGACAM_APER = set_column_properties(
            "MAGERR_U_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAGERR_G_EXT_OMEGACAM_APER = set_column_properties(
            "MAGERR_G_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAGERR_R_EXT_OMEGACAM_APER = set_column_properties(
            "MAGERR_R_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.MAGERR_I_EXT_OMEGACAM_APER = set_column_properties(
            "MAGERR_I_EXT_OMEGACAM_APER", is_optional=True, comment=None)

        self.MAGERR_U_EXT_LSST_APER = set_column_properties("MAGERR_U_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAGERR_G_EXT_LSST_APER = set_column_properties("MAGERR_G_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAGERR_R_EXT_LSST_APER = set_column_properties("MAGERR_R_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAGERR_I_EXT_LSST_APER = set_column_properties("MAGERR_I_EXT_LSST_APER", is_optional=True, comment=None)
        self.MAGERR_Z_EXT_LSST_APER = set_column_properties("MAGERR_Z_EXT_LSST_APER", is_optional=True, comment=None)

        self.MAGERR_VIS_APER = set_column_properties("MAGERR_VIS_APER", is_optional=True, comment=None)
        self.MAGERR_Y_APER = set_column_properties("MAGERR_Y_APER", is_optional=True, comment=None)
        self.MAGERR_J_APER = set_column_properties("MAGERR_J_APER", is_optional=True, comment=None)
        self.MAGERR_H_APER = set_column_properties("MAGERR_H_APER", is_optional=True, comment=None)

        self.SN_G_EXT_DECAM_APER = set_column_properties("SN_G_EXT_DECAM_APER", is_optional=True, comment=None)
        self.SN_R_EXT_DECAM_APER = set_column_properties("SN_R_EXT_DECAM_APER", is_optional=True, comment=None)
        self.SN_I_EXT_DECAM_APER = set_column_properties("SN_I_EXT_DECAM_APER", is_optional=True, comment=None)
        self.SN_Z_EXT_DECAM_APER = set_column_properties("SN_Z_EXT_DECAM_APER", is_optional=True, comment=None)

        self.SN_U_EXT_OMEGACAM_APER = set_column_properties("SN_U_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.SN_G_EXT_OMEGACAM_APER = set_column_properties("SN_G_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.SN_R_EXT_OMEGACAM_APER = set_column_properties("SN_R_EXT_OMEGACAM_APER", is_optional=True, comment=None)
        self.SN_I_EXT_OMEGACAM_APER = set_column_properties("SN_I_EXT_OMEGACAM_APER", is_optional=True, comment=None)

        self.SN_U_EXT_LSST_APER = set_column_properties("SN_U_EXT_LSST_APER", is_optional=True, comment=None)
        self.SN_G_EXT_LSST_APER = set_column_properties("SN_G_EXT_LSST_APER", is_optional=True, comment=None)
        self.SN_R_EXT_LSST_APER = set_column_properties("SN_R_EXT_LSST_APER", is_optional=True, comment=None)
        self.SN_I_EXT_LSST_APER = set_column_properties("SN_I_EXT_LSST_APER", is_optional=True, comment=None)
        self.SN_Z_EXT_LSST_APER = set_column_properties("SN_Z_EXT_LSST_APER", is_optional=True, comment=None)

        self.SN_VIS_APER = set_column_properties("SN_VIS_APER", is_optional=True, comment=None)
        self.SN_Y_APER = set_column_properties("SN_Y_APER", is_optional=True, comment=None)
        self.SN_J_APER = set_column_properties("SN_J_APER", is_optional=True, comment=None)
        self.SN_H_APER = set_column_properties("SN_H_APER", is_optional=True, comment=None)

        self.MAG_G_EXT_DECAM_TOTAL = set_column_properties("MAG_G_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAG_R_EXT_DECAM_TOTAL = set_column_properties("MAG_R_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAG_I_EXT_DECAM_TOTAL = set_column_properties("MAG_I_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAG_Z_EXT_DECAM_TOTAL = set_column_properties("MAG_Z_EXT_DECAM_TOTAL", is_optional=True, comment=None)

        self.MAG_U_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAG_U_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAG_G_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAG_G_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAG_R_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAG_R_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAG_I_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAG_I_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)

        self.MAG_U_EXT_LSST_TOTAL = set_column_properties("MAG_U_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAG_G_EXT_LSST_TOTAL = set_column_properties("MAG_G_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAG_R_EXT_LSST_TOTAL = set_column_properties("MAG_R_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAG_I_EXT_LSST_TOTAL = set_column_properties("MAG_I_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAG_Z_EXT_LSST_TOTAL = set_column_properties("MAG_Z_EXT_LSST_TOTAL", is_optional=True, comment=None)

        self.MAG_VIS_TOTAL = set_column_properties("MAG_VIS_TOTAL", is_optional=True, comment=None)
        self.MAG_Y_TOTAL = set_column_properties("MAG_Y_TOTAL", is_optional=True, comment=None)
        self.MAG_J_TOTAL = set_column_properties("MAG_J_TOTAL", is_optional=True, comment=None)
        self.MAG_H_TOTAL = set_column_properties("MAG_H_TOTAL", is_optional=True, comment=None)

        self.MAG_NIR_STACK_APER = set_column_properties("MAG_NIR_STACK_APER", is_optional=True, comment=None)
        self.MAGERR_NIR_STACK_APER = set_column_properties("MAGERR_NIR_STACK_APER", is_optional=True, comment=None)
        self.SN_NIR_STACK_APER = set_column_properties("SN_NIR_STACK_APER", is_optional=True, comment=None)

        self.MAGERR_G_EXT_DECAM_TOTAL = set_column_properties(
            "MAGERR_G_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_R_EXT_DECAM_TOTAL = set_column_properties(
            "MAGERR_R_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_I_EXT_DECAM_TOTAL = set_column_properties(
            "MAGERR_I_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_Z_EXT_DECAM_TOTAL = set_column_properties(
            "MAGERR_Z_EXT_DECAM_TOTAL", is_optional=True, comment=None)

        self.MAGERR_U_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAGERR_U_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_G_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAGERR_G_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_R_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAGERR_R_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.MAGERR_I_EXT_OMEGACAM_TOTAL = set_column_properties(
            "MAGERR_I_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)

        self.MAGERR_U_EXT_LSST_TOTAL = set_column_properties("MAGERR_U_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAGERR_G_EXT_LSST_TOTAL = set_column_properties("MAGERR_G_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAGERR_R_EXT_LSST_TOTAL = set_column_properties("MAGERR_R_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAGERR_I_EXT_LSST_TOTAL = set_column_properties("MAGERR_I_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.MAGERR_Z_EXT_LSST_TOTAL = set_column_properties("MAGERR_Z_EXT_LSST_TOTAL", is_optional=True, comment=None)

        self.MAGERR_VIS_TOTAL = set_column_properties("MAGERR_VIS_TOTAL", is_optional=True, comment=None)
        self.MAGERR_Y_TOTAL = set_column_properties("MAGERR_Y_TOTAL", is_optional=True, comment=None)
        self.MAGERR_J_TOTAL = set_column_properties("MAGERR_J_TOTAL", is_optional=True, comment=None)
        self.MAGERR_H_TOTAL = set_column_properties("MAGERR_H_TOTAL", is_optional=True, comment=None)

        self.SN_G_EXT_DECAM_TOTAL = set_column_properties("SN_G_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.SN_R_EXT_DECAM_TOTAL = set_column_properties("SN_R_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.SN_I_EXT_DECAM_TOTAL = set_column_properties("SN_I_EXT_DECAM_TOTAL", is_optional=True, comment=None)
        self.SN_Z_EXT_DECAM_TOTAL = set_column_properties("SN_Z_EXT_DECAM_TOTAL", is_optional=True, comment=None)

        self.SN_U_EXT_OMEGACAM_TOTAL = set_column_properties("SN_U_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.SN_G_EXT_OMEGACAM_TOTAL = set_column_properties("SN_G_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.SN_R_EXT_OMEGACAM_TOTAL = set_column_properties("SN_R_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)
        self.SN_I_EXT_OMEGACAM_TOTAL = set_column_properties("SN_I_EXT_OMEGACAM_TOTAL", is_optional=True, comment=None)

        self.SN_U_EXT_LSST_TOTAL = set_column_properties("SN_U_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.SN_G_EXT_LSST_TOTAL = set_column_properties("SN_G_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.SN_R_EXT_LSST_TOTAL = set_column_properties("SN_R_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.SN_I_EXT_LSST_TOTAL = set_column_properties("SN_I_EXT_LSST_TOTAL", is_optional=True, comment=None)
        self.SN_Z_EXT_LSST_TOTAL = set_column_properties("SN_Z_EXT_LSST_TOTAL", is_optional=True, comment=None)

        self.SN_VIS_TOTAL = set_column_properties("SN_VIS_TOTAL", is_optional=True, comment=None)
        self.SN_Y_TOTAL = set_column_properties("SN_Y_TOTAL", is_optional=True, comment=None)
        self.SN_J_TOTAL = set_column_properties("SN_J_TOTAL", is_optional=True, comment=None)
        self.SN_H_TOTAL = set_column_properties("SN_H_TOTAL", is_optional=True, comment=None)

        self.MAG_VIS_PSF = set_column_properties("MAG_VIS_PSF", is_optional=True, comment=None)
        self.MAGERR_VIS_PSF = set_column_properties("MAGERR_VIS_PSF", is_optional=True, comment=None)
        self.SN_VIS_PSF = set_column_properties("SN_VIS_PSF", is_optional=True, comment=None)

        self.MAG_DETECTION_TOTAL = set_column_properties("MAG_DETECTION_TOTAL", is_optional=True, comment=None)
        self.MAGERR_DETECTION_TOTAL = set_column_properties("MAGERR_DETECTION_TOTAL", is_optional=True, comment=None)
        self.SN_DETECTION_TOTAL = set_column_properties("SN_DETECTION_TOTAL", is_optional=True, comment=None)

        self.VARIABILITY_FLAG = set_column_properties("VARIABILITY_FLAG", is_optional=True, comment=None)
        self.BINARY_FLAG = set_column_properties("BINARY_FLAG", is_optional=True, comment=None)
        self.STAR_FLAG = set_column_properties("STAR_FLAG", is_optional=True, comment=None)
        self.STAR_PROB = set_column_properties("STAR_PROB", is_optional=True, comment=None)
        self.MAG_STARGAL_SEP = set_column_properties("MAG_STARGAL_SEP", is_optional=True, comment=None)
        self.DET_QUALITY_FLAG = set_column_properties("DET_QUALITY_FLAG", is_optional=True, comment=None)
        self.MU_MAX = set_column_properties("MU_MAX", is_optional=True, comment=None)

        self.Isoarea = set_column_properties(
            "Isoarea", is_optional=True, comment=None)

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


def make_detections_table_header(model_hash=None,
                                 model_seed=None,
                                 noise_seed=None):
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


def initialise_detections_table(image_group_phl=None,
                                options=None,
                                optional_columns=None,
                                model_hash=None,
                                model_seed=None,
                                noise_seed=None):
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

    detections_table = Table(init_cols, names=names,
                             dtype=dtypes)

    if image_group_phl is not None:

        # Get values from the image object, unless they were passed explicitly

        if model_seed is None:
            model_seed = image_group_phl.get_seed()

    if options is not None:

        # Get values from the options dict, unless they were passed explicitly

        if model_hash is None:
            model_hash = hash_any(options.items(), format="base64")
        if noise_seed is None:
            noise_seed = options['noise_seed']

    detections_table.meta = make_detections_table_header(model_hash=model_hash,
                                                         model_seed=model_seed,
                                                         noise_seed=noise_seed)

    assert(is_in_format(detections_table, tf))

    return detections_table
