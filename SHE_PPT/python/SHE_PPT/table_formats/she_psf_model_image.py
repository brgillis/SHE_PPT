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

__updated__ = "2021-08-13"

from collections import OrderedDict

from ..constants.fits import EXTNAME_LABEL, FITS_DEF_LABEL, FITS_VERSION_LABEL, PSF_CAT_TAG
from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.psfModelImage.shePsfC"

logger = getLogger(__name__)


class ShePsfModelImageMeta(SheTableMeta):
    """
        @brief A class defining the metadata for PSF tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    extname: str = EXTNAME_LABEL

    calibration_product: str = "CAL_PROD"
    calibration_time: str = "CAL_TIME"
    field_product: str = "FLD_PROD"
    field_time: str = "FLD_TIME"

    def __init__(self):
        super().__init__(comments=OrderedDict(((self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.extname, PSF_CAT_TAG),
                                               (self.calibration_product, None),
                                               (self.calibration_time, None),
                                               (self.field_product, None),
                                               (self.field_time, None)
                                               )))

    def init_meta(self, **kwargs: str):
        return super().init_meta(extname=PSF_CAT_TAG,
                                 **kwargs)


class ShePsfModelImageFormat(SheTableFormat):
    """
        @brief A class defining the format for detections tables. Only the psf_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = ShePsfModelImageMeta

    def __init__(self):
        super().__init__()

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

        self._finalize_init()


# Define an instance of this object that can be imported
psf_table_format = ShePsfModelImageFormat()

# And a convenient alias for it
tf = psf_table_format
