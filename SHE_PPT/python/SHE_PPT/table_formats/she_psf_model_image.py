""" @file psf.py

    Created 29 Sep 2017

    Format definition for PSF table. This is based on Chris's description in the DPDD.
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

__updated__ = "2019-02-27"

from collections import OrderedDict

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import hash_any
from astropy.table import Table
import numpy as np


logger = getLogger(mv.logger_name)


class PSFTableMeta(object):
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = "she.psfModelImage.shePsfC"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.extname = mv.extname_label

        #self.model_hash = mv.model_hash_label
        #self.model_seed = mv.model_seed_label
        #self.noise_seed = mv.noise_seed_label
        self.cal_prod = "CAL_PROD"
        self.cal_time = "CAL_TIME"
        self.fld_prod = "FLD_PROD"
        self.fld_time = "FLD_TIME"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, mv.psf_cat_tag),
                                     (self.cal_prod, None),
                                     (self.cal_time, None),
                                     (self.fld_prod, None),
                                     (self.fld_time,None)
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class PSFTableFormat(object):
    """
        @brief A class defining the format for detections tables. Only the psf_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = PSFTableMeta()

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

        self.ID = set_column_properties(
            "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.template = set_column_properties(
            "SHE_PSF_SED_TEMPLATE", dtype=">i8", fits_dtype="K")
        self.bulge_idx = set_column_properties(
            "SHE_PSF_BULGE_IDX", dtype=">i4", fits_dtype="J")
        self.disk_idx = set_column_properties(
            "SHE_PSF_DISK_IDX", dtype=">i4", fits_dtype="J")
        self.image_x = set_column_properties(
            "SHE_PSF_IMAGE_X", dtype=">i2", fits_dtype="I")
        self.image_y = set_column_properties(
            "SHE_PSF_IMAGE_Y", dtype=">i2", fits_dtype="I")
        self.x = set_column_properties(
            "SHE_PSF_X", dtype=">f4", fits_dtype="E")
        self.y = set_column_properties(
            "SHE_PSF_Y", dtype=">f4", fits_dtype="E")
       
        self.cal_time = set_column_properties(
            "SHE_PSF_CALIB_TIME", dtype="str", fits_dtype="A", length=20)
        self.field_time = set_column_properties(
            "SHE_PSF_FIELD_TIME", dtype="str", fits_dtype="A", length=20)

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
psf_table_format = PSFTableFormat()

# And a convient alias for it
tf = psf_table_format


def make_psf_table_header(cal_prod,cal_time,fld_prod,fld_time):
    """
        @brief Generate a header for a PSF table.

        @param detector <int?> Detector for this image, if applicable

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.extname] = mv.psf_cat_tag

    header[tf.m.cal_prod] = cal_prod
    header[tf.m.cal_time] = cal_time
    header[tf.m.fld_prod] = fld_prod
    header[tf.m.fld_time] = fld_time
    
    
    return header


def initialise_psf_table(image=None,
                         options=None,
                         optional_columns=None,
                         cal_prod=None,
                         cal_time=None,
                         fld_prod=None,
                         fld_time=None,
                         init_columns={}):
    """
        @brief Initialise a PSF table.

        @param image <SHE_SIM.Image>

        @param options <dict> Options dictionary

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is psf_x and psf_y

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

            dtype = (tf.dtypes[colname], tf.lengths[colname])

            if colname in init_columns:
                init_cols.append(init_columns[colname])
            elif len(init_columns) > 0:
                init_cols.append(
                    np.zeros(len(init_columns.values[0]), dtype=dtype))
            else:
                init_cols.append([])

            dtypes.append(dtype)

    psf_table = Table(init_cols, names=names, dtype=dtypes)
    

    psf_table.meta = make_psf_table_header(cal_prod=cal_prod,
                                           cal_time=cal_time,
                                           fld_prod=fld_prod,
                                           fld_time=fld_time)

    assert(is_in_format(psf_table, tf))

    return psf_table
