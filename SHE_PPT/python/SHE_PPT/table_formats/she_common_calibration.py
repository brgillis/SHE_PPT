""" @file common_calibration.py

    Created 6 Dec 2017

    Format definition for common calibration tables.
"""

__updated__ = "2021-08-12"

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

from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.commonCalibration"

logger = getLogger(__name__)


class SheCommonCalibrationMeta(SheTableMeta):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def


class SheCommonCalibrationFormat(SheTableFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the common_calibration_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheCommonCalibrationMeta())

        # Table column labels and properties

        self.f0_min = self.set_column_properties(
            "SHE_CC_F0_MIN", dtype = ">f4", fits_dtype = "E")
        self.f0_max = self.set_column_properties(
            "SHE_CC_F0_MAX", dtype = ">f4", fits_dtype = "E")
        self.f1_min = self.set_column_properties(
            "SHE_CC_F1_MIN", dtype = ">f4", fits_dtype = "E")
        self.f1_max = self.set_column_properties(
            "SHE_CC_F1_MAX", dtype = ">f4", fits_dtype = "E")
        self.f2_min = self.set_column_properties(
            "SHE_CC_F2_MIN", dtype = ">f4", fits_dtype = "E")
        self.f2_max = self.set_column_properties(
            "SHE_CC_F2_MAX", dtype = ">f4", fits_dtype = "E")
        self.f3_min = self.set_column_properties(
            "SHE_CC_F3_MIN", dtype = ">f4", fits_dtype = "E")
        self.f3_max = self.set_column_properties(
            "SHE_CC_F3_MAX", dtype = ">f4", fits_dtype = "E")
        self.f4_min = self.set_column_properties(
            "SHE_CC_F4_MIN", dtype = ">f4", fits_dtype = "E")
        self.f4_max = self.set_column_properties(
            "SHE_CC_F4_MAX", dtype = ">f4", fits_dtype = "E")
        self.f5_min = self.set_column_properties(
            "SHE_CC_F5_MIN", dtype = ">f4", fits_dtype = "E")
        self.f5_max = self.set_column_properties(
            "SHE_CC_F5_MAX", dtype = ">f4", fits_dtype = "E")
        self.f6_min = self.set_column_properties(
            "SHE_CC_F6_MIN", dtype = ">f4", fits_dtype = "E")
        self.f6_max = self.set_column_properties(
            "SHE_CC_F6_MAX", dtype = ">f4", fits_dtype = "E")
        self.f7_min = self.set_column_properties(
            "SHE_CC_F7_MIN", dtype = ">f4", fits_dtype = "E")
        self.f7_max = self.set_column_properties(
            "SHE_CC_F7_MAX", dtype = ">f4", fits_dtype = "E")
        self.f8_min = self.set_column_properties(
            "SHE_CC_F8_MIN", dtype = ">f4", fits_dtype = "E")
        self.f8_max = self.set_column_properties(
            "SHE_CC_F8_MAX", dtype = ">f4", fits_dtype = "E")
        self.f9_min = self.set_column_properties(
            "SHE_CC_F9_MIN", dtype = ">f4", fits_dtype = "E")
        self.f9_max = self.set_column_properties(
            "SHE_CC_F9_MAX", dtype = ">f4", fits_dtype = "E")
        self.i0_min = self.set_column_properties(
            "SHE_CC_I0_MIN", dtype = ">i8", fits_dtype = "K")
        self.i0_max = self.set_column_properties(
            "SHE_CC_I0_MAX", dtype = ">i8", fits_dtype = "K")
        self.i1_min = self.set_column_properties(
            "SHE_CC_I1_MIN", dtype = ">i8", fits_dtype = "K")
        self.i1_max = self.set_column_properties(
            "SHE_CC_I1_MAX", dtype = ">i8", fits_dtype = "K")
        self.i2_min = self.set_column_properties(
            "SHE_CC_I2_MIN", dtype = ">i8", fits_dtype = "K")
        self.i2_max = self.set_column_properties(
            "SHE_CC_I2_MAX", dtype = ">i8", fits_dtype = "K")
        self.i3_min = self.set_column_properties(
            "SHE_CC_I3_MIN", dtype = ">i8", fits_dtype = "K")
        self.i3_max = self.set_column_properties(
            "SHE_CC_I3_MAX", dtype = ">i8", fits_dtype = "K")
        self.i4_min = self.set_column_properties(
            "SHE_CC_I4_MIN", dtype = ">i8", fits_dtype = "K")
        self.i4_max = self.set_column_properties(
            "SHE_CC_I4_MAX", dtype = ">i8", fits_dtype = "K")
        self.i5_min = self.set_column_properties(
            "SHE_CC_I5_MIN", dtype = ">i8", fits_dtype = "K")
        self.i5_max = self.set_column_properties(
            "SHE_CC_I5_MAX", dtype = ">i8", fits_dtype = "K")
        self.i6_min = self.set_column_properties(
            "SHE_CC_I6_MIN", dtype = ">i8", fits_dtype = "K")
        self.i6_max = self.set_column_properties(
            "SHE_CC_I6_MAX", dtype = ">i8", fits_dtype = "K")
        self.i7_min = self.set_column_properties(
            "SHE_CC_I7_MIN", dtype = ">i8", fits_dtype = "K")
        self.i7_max = self.set_column_properties(
            "SHE_CC_I7_MAX", dtype = ">i8", fits_dtype = "K")
        self.i8_min = self.set_column_properties(
            "SHE_CC_I8_MIN", dtype = ">i8", fits_dtype = "K")
        self.i8_max = self.set_column_properties(
            "SHE_CC_I8_MAX", dtype = ">i8", fits_dtype = "K")
        self.i9_min = self.set_column_properties(
            "SHE_CC_I9_MIN", dtype = ">i8", fits_dtype = "K")
        self.i9_max = self.set_column_properties(
            "SHE_CC_I9_MAX", dtype = ">i8", fits_dtype = "K")
        self.m1 = self.set_column_properties(
            "SHE_CC_M1", dtype = ">f4", fits_dtype = "E")
        self.m1_err = self.set_column_properties(
            "SHE_CC_M1_ERR", dtype = ">f4", fits_dtype = "E")
        self.m2 = self.set_column_properties(
            "SHE_CC_M2", dtype = ">f4", fits_dtype = "E")
        self.m2_err = self.set_column_properties(
            "SHE_CC_M2_ERR", dtype = ">f4", fits_dtype = "E")
        self.c1 = self.set_column_properties(
            "SHE_CC_C1", dtype = ">f4", fits_dtype = "E")
        self.c1_err = self.set_column_properties(
            "SHE_CC_C1_ERR", dtype = ">f4", fits_dtype = "E")
        self.c2 = self.set_column_properties(
            "SHE_CC_C2", dtype = ">f4", fits_dtype = "E")
        self.c2_err = self.set_column_properties(
            "SHE_CC_C2_ERR", dtype = ">f4", fits_dtype = "E")

        self._finalize_init()


# Define an instance of this object that can be imported
common_calibration_table_format = SheCommonCalibrationFormat()

# And a convenient alias for it
tf = common_calibration_table_format
