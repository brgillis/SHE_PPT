""" @file common_calibration.py

    Created 6 Dec 2017

    Format definition for common calibration tables.
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

__updated__ = "2020-07-19"

from collections import OrderedDict


from ..constants.fits import fits_version_label, fits_def_label, extname_label
from ..logging import getLogger
from ..table_formats.mer_final_catalog import tf as mfc_tf
from ..table_utility import is_in_format, init_table, SheTableFormat


fits_version = "8.0"
fits_def = "she.commonCalibration"

logger = getLogger(__name__)


class SheCommonCalibrationMeta():
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheCommonCalibrationFormat(SheTableFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the common_calibration_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheCommonCalibrationMeta())

        # Table column labels and properties

        self.f0_min = self.set_column_properties(
                                            "SHE_CC_F0_MIN", dtype=">f4", fits_dtype="E")
        self.f0_max = self.set_column_properties(
                                            "SHE_CC_F0_MAX", dtype=">f4", fits_dtype="E")
        self.f1_min = self.set_column_properties(
                                            "SHE_CC_F1_MIN", dtype=">f4", fits_dtype="E")
        self.f1_max = self.set_column_properties(
                                            "SHE_CC_F1_MAX", dtype=">f4", fits_dtype="E")
        self.f2_min = self.set_column_properties(
                                            "SHE_CC_F2_MIN", dtype=">f4", fits_dtype="E")
        self.f2_max = self.set_column_properties(
                                            "SHE_CC_F2_MAX", dtype=">f4", fits_dtype="E")
        self.f3_min = self.set_column_properties(
                                            "SHE_CC_F3_MIN", dtype=">f4", fits_dtype="E")
        self.f3_max = self.set_column_properties(
                                            "SHE_CC_F3_MAX", dtype=">f4", fits_dtype="E")
        self.f4_min = self.set_column_properties(
                                            "SHE_CC_F4_MIN", dtype=">f4", fits_dtype="E")
        self.f4_max = self.set_column_properties(
                                            "SHE_CC_F4_MAX", dtype=">f4", fits_dtype="E")
        self.f5_min = self.set_column_properties(
                                            "SHE_CC_F5_MIN", dtype=">f4", fits_dtype="E")
        self.f5_max = self.set_column_properties(
                                            "SHE_CC_F5_MAX", dtype=">f4", fits_dtype="E")
        self.f6_min = self.set_column_properties(
                                            "SHE_CC_F6_MIN", dtype=">f4", fits_dtype="E")
        self.f6_max = self.set_column_properties(
                                            "SHE_CC_F6_MAX", dtype=">f4", fits_dtype="E")
        self.f7_min = self.set_column_properties(
                                            "SHE_CC_F7_MIN", dtype=">f4", fits_dtype="E")
        self.f7_max = self.set_column_properties(
                                            "SHE_CC_F7_MAX", dtype=">f4", fits_dtype="E")
        self.f8_min = self.set_column_properties(
                                            "SHE_CC_F8_MIN", dtype=">f4", fits_dtype="E")
        self.f8_max = self.set_column_properties(
                                            "SHE_CC_F8_MAX", dtype=">f4", fits_dtype="E")
        self.f9_min = self.set_column_properties(
                                            "SHE_CC_F9_MIN", dtype=">f4", fits_dtype="E")
        self.f9_max = self.set_column_properties(
                                            "SHE_CC_F9_MAX", dtype=">f4", fits_dtype="E")
        self.i0_min = self.set_column_properties(
                                            "SHE_CC_I0_MIN", dtype=">i8", fits_dtype="K")
        self.i0_max = self.set_column_properties(
                                            "SHE_CC_I0_MAX", dtype=">i8", fits_dtype="K")
        self.i1_min = self.set_column_properties(
                                            "SHE_CC_I1_MIN", dtype=">i8", fits_dtype="K")
        self.i1_max = self.set_column_properties(
                                            "SHE_CC_I1_MAX", dtype=">i8", fits_dtype="K")
        self.i2_min = self.set_column_properties(
                                            "SHE_CC_I2_MIN", dtype=">i8", fits_dtype="K")
        self.i2_max = self.set_column_properties(
                                            "SHE_CC_I2_MAX", dtype=">i8", fits_dtype="K")
        self.i3_min = self.set_column_properties(
                                            "SHE_CC_I3_MIN", dtype=">i8", fits_dtype="K")
        self.i3_max = self.set_column_properties(
                                            "SHE_CC_I3_MAX", dtype=">i8", fits_dtype="K")
        self.i4_min = self.set_column_properties(
                                            "SHE_CC_I4_MIN", dtype=">i8", fits_dtype="K")
        self.i4_max = self.set_column_properties(
                                            "SHE_CC_I4_MAX", dtype=">i8", fits_dtype="K")
        self.i5_min = self.set_column_properties(
                                            "SHE_CC_I5_MIN", dtype=">i8", fits_dtype="K")
        self.i5_max = self.set_column_properties(
                                            "SHE_CC_I5_MAX", dtype=">i8", fits_dtype="K")
        self.i6_min = self.set_column_properties(
                                            "SHE_CC_I6_MIN", dtype=">i8", fits_dtype="K")
        self.i6_max = self.set_column_properties(
                                            "SHE_CC_I6_MAX", dtype=">i8", fits_dtype="K")
        self.i7_min = self.set_column_properties(
                                            "SHE_CC_I7_MIN", dtype=">i8", fits_dtype="K")
        self.i7_max = self.set_column_properties(
                                            "SHE_CC_I7_MAX", dtype=">i8", fits_dtype="K")
        self.i8_min = self.set_column_properties(
                                            "SHE_CC_I8_MIN", dtype=">i8", fits_dtype="K")
        self.i8_max = self.set_column_properties(
                                            "SHE_CC_I8_MAX", dtype=">i8", fits_dtype="K")
        self.i9_min = self.set_column_properties(
                                            "SHE_CC_I9_MIN", dtype=">i8", fits_dtype="K")
        self.i9_max = self.set_column_properties(
                                            "SHE_CC_I9_MAX", dtype=">i8", fits_dtype="K")
        self.m1 = self.set_column_properties(
                                        "SHE_CC_M1", dtype=">f4", fits_dtype="E")
        self.m1_err = self.set_column_properties(
                                            "SHE_CC_M1_ERR", dtype=">f4", fits_dtype="E")
        self.m2 = self.set_column_properties(
                                        "SHE_CC_M2", dtype=">f4", fits_dtype="E")
        self.m2_err = self.set_column_properties(
                                            "SHE_CC_M2_ERR", dtype=">f4", fits_dtype="E")
        self.c1 = self.set_column_properties(
                                        "SHE_CC_C1", dtype=">f4", fits_dtype="E")
        self.c1_err = self.set_column_properties(
                                            "SHE_CC_C1_ERR", dtype=">f4", fits_dtype="E")
        self.c2 = self.set_column_properties(
                                        "SHE_CC_C2", dtype=">f4", fits_dtype="E")
        self.c2_err = self.set_column_properties(
                                            "SHE_CC_C2_ERR", dtype=">f4", fits_dtype="E")

        self._finalize_init()


# Define an instance of this object that can be imported
common_calibration_table_format = SheCommonCalibrationFormat()

# And a convient alias for it
tf = common_calibration_table_format


def make_common_calibration_table_header():
    """
        @brief Generate a header for a shear estimates table.

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @return header <dict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    return header


def initialise_common_calibration_table(mer_final_catalog=None,
                                        size=None,
                                        optional_columns=None,
                                        init_cols=None,
                                        ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param mer_final_catalog <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param detector <int?> Detector this table corresponds to

        @return common_calibration_table <astropy.table.Table>
    """

    assert (mer_final_catalog is None) or (
        is_in_format(mer_final_catalog, mfc_tf, strict=False))

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    common_calibration_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    common_calibration_table.meta = make_common_calibration_table_header()

    assert is_in_format(common_calibration_table, tf)

    return common_calibration_table
