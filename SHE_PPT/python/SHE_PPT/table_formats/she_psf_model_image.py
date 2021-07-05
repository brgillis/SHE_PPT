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

__updated__ = "2021-02-10"

from collections import OrderedDict

from .. import magic_values as mv
from ..logging import getLogger
from ..table_utility import is_in_format, init_table,SheTableFormat


fits_version = "8.0"
fits_def = "she.psfModelImage.shePsfC"

logger = getLogger(mv.logger_name)


class ShePsfModelImageMeta():
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.extname = mv.extname_label

        self.calibration_product = "CAL_PROD"
        self.calibration_time = "CAL_TIME"
        self.field_product = "FLD_PROD"
        self.field_time = "FLD_TIME"

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.extname, mv.psf_cat_tag),
                                     (self.calibration_product, None),
                                     (self.calibration_time, None),
                                     (self.field_product, None),
                                     (self.field_time, None)
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class ShePsfModelImageFormat(SheTableFormat):
    """
        @brief A class defining the format for detections tables. Only the psf_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(ShePsfModelImageMeta())

        # Column names and info

        self.ID = self.set_column_properties(
                                        "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.template = self.set_column_properties(
                                              "SHE_PSF_SED_TEMPLATE", dtype=">i8", fits_dtype="K")
        self.bulge_index = self.set_column_properties(
                                                 "SHE_PSF_BULGE_INDEX", dtype=">i4", fits_dtype="J")
        self.disk_index = self.set_column_properties(
                                                "SHE_PSF_DISK_INDEX", dtype=">i4", fits_dtype="J")
        self.image_x = self.set_column_properties(
                                             "SHE_PSF_IMAGE_X", dtype=">i2", fits_dtype="I")
        self.image_y = self.set_column_properties(
                                             "SHE_PSF_IMAGE_Y", dtype=">i2", fits_dtype="I")
        self.x = self.set_column_properties(
                                       "SHE_PSF_X", dtype=">f4", fits_dtype="E")
        self.y = self.set_column_properties(
                                       "SHE_PSF_Y", dtype=">f4", fits_dtype="E")

        self.calibration_time = self.set_column_properties(
                                                      "SHE_PSF_CALIB_TIME", dtype="str", fits_dtype="A", length=20)
        self.field_time = self.set_column_properties(
                                                "SHE_PSF_FIELD_TIME", dtype="str", fits_dtype="A", length=20)
        self.qual_flag = self.set_column_properties(
                                               "SHE_PSF_QUAL_FLAG", dtype=">i4", fits_dtype="J")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
psf_table_format = ShePsfModelImageFormat()

# And a convient alias for it
tf = psf_table_format


def make_psf_table_header(calibration_product, calibration_time, field_product, field_time):
    """
        @brief Generate a header for a PSF table.

        @param detector <int?> Detector for this image, if applicable

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    header[tf.m.extname] = mv.psf_cat_tag

    header[tf.m.calibration_product] = calibration_product
    header[tf.m.calibration_time] = calibration_time
    header[tf.m.field_product] = field_product
    header[tf.m.field_time] = field_time

    return header


def initialise_psf_table(size=None,
                         optional_columns=None,
                         calibration_product=None,
                         calibration_time=None,
                         field_product=None,
                         field_time=None,
                         init_cols={}):
    """
        @brief Initialise a PSF table.

        @param image <SHE_SIM.Image>

        @param options <dict> Options dictionary

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is psf_x and psf_y

        @return mer_final_catalog <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    psf_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    psf_table.meta = make_psf_table_header(calibration_product=calibration_product,
                                           calibration_time=calibration_time,
                                           field_product=field_product,
                                           field_time=field_time)

    assert is_in_format(psf_table, tf)

    return psf_table
