""" @file star_catalog.py

    Created 23 July 2018

    Format definition for a table containing Star Catalog data.
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

from ..constants.fits import FITS_DEF_LABEL, FITS_VERSION_LABEL, OBS_ID_LABEL, OBS_TIME_LABEL
from ..table_utility import SheTableFormat, SheTableMeta

fits_version: str = "8.0"
fits_def: str = "she.starCatalog"


class SheStarCatalogMeta(SheTableMeta):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    roll_ang: str = "ROLLANGL"
    exposure_product_id: str = "EXP_PID"
    observation_id: str = OBS_ID_LABEL
    observation_time: str = OBS_TIME_LABEL


class SheStarCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for SHE star catalog tables. Only the star_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = SheStarCatalogMeta

    def __init__(self):
        super().__init__()

        # Column names and info

        self.id = self.set_column_properties(
            "OBJECT_ID", dtype=">i8", fits_dtype="K",
            comment="ID of this object in the galaxy population priors table.")

        self.det_x = self.set_column_properties(
            "SHE_STARCAT_DET_X", dtype=">i4", fits_dtype="I")
        self.det_y = self.set_column_properties(
            "SHE_STARCAT_DET_Y", dtype=">i4", fits_dtype="I")
        self.x = self.set_column_properties(
            "SHE_STARCAT_X", dtype=">f4", fits_dtype="E")
        self.x_err = self.set_column_properties(
            "SHE_STARCAT_X_ERR", dtype=">f4", fits_dtype="E")
        self.y = self.set_column_properties(
            "SHE_STARCAT_Y", dtype=">f4", fits_dtype="E")
        self.y_err = self.set_column_properties(
            "SHE_STARCAT_Y_ERR", dtype=">f4", fits_dtype="E")
        self.ra = self.set_column_properties(
            "SHE_STARCAT_UPDATED_RA", comment="deg", dtype=">f8", fits_dtype="D")
        self.ra_err = self.set_column_properties(
            "SHE_STARCAT_UPDATED_RA_ERR", comment="deg", dtype=">f8", fits_dtype="E")
        self.dec = self.set_column_properties(
            "SHE_STARCAT_UPDATED_DEC", comment="deg", dtype=">f8", fits_dtype="D")
        self.dec_err = self.set_column_properties(
            "SHE_STARCAT_UPDATED_DEC_ERR", comment="deg", dtype=">f8", fits_dtype="E")
        self.flux = self.set_column_properties(
            "SHE_STARCAT_FLUX", dtype=">f4", fits_dtype="E")
        self.flux_err = self.set_column_properties(
            "SHE_STARCAT_FLUX_ERR", dtype=">f4", fits_dtype="E")

        self.e1 = self.set_column_properties("SHE_STARCAT_E1", dtype=">f4", fits_dtype="E",
                                             comment="Mean ellipticity measurement of this object, component 1")
        self.e2 = self.set_column_properties("SHE_STARCAT_E2", dtype=">f4", fits_dtype="E",
                                             comment="Mean ellipticity measurement of this object, component 2")
        self.e1_err = self.set_column_properties("SHE_STARCAT_E1_ERR", dtype=">f4", fits_dtype="E",
                                                 comment="Error on mean ellipticity measurement of this object, "
                                                         "component 1")
        self.e2_err = self.set_column_properties("SHE_STARCAT_E2_ERR", dtype=">f4", fits_dtype="E",
                                                 comment="Error on mean ellipticity measurement of this object, "
                                                         "component 2")

        self.used_for_fit = self.set_column_properties("SHE_STARCAT_USED_FOR_FIT", dtype="bool", fits_dtype="L",
                                                       comment="Whether or not this star was used for fitting "
                                                               "the PSF model.")
        self.group_id = self.set_column_properties("SHE_STARCAT_GROUP_ID", dtype=">i8", fits_dtype="K",
                                                   comment="A unique ID for the group of stars fitted "
                                                           "simultaneously, generally the ID of one of the stars "
                                                           "in the group to avoid duplication.")
        self.group_chisq = self.set_column_properties("SHE_STARCAT_GROUP_CHISQ", dtype=">f4", fits_dtype="E",
                                                      comment="Chi-squared statistic for the residual of the "
                                                              "fitted or modeled group of PSFs compared to the stars")
        self.group_unmasked_pix = self.set_column_properties("SHE_STARCAT_GROUP_UNMASKED_PIX", dtype=">i4",
                                                             fits_dtype="J",
                                                             comment="Total number of unmasked pixels covered by "
                                                                     "stars in this group.")
        self.group_num_fitted_params = self.set_column_properties("SHE_STARCAT_GROUP_N_FITTED_PARAMS", dtype=">i4",
                                                                  fits_dtype="J",
                                                                  comment="Number of fitted parameters of the PSF "
                                                                          "model "
                                                                          "for this group of stars")
        self.star_chisq = self.set_column_properties("SHE_STARCAT_STAR_CHISQ", dtype=">f4", fits_dtype="E",
                                                     comment="Chi-squared statistic for the residual of the "
                                                             "fitted or modeled PSF compared to this star.")
        self.star_unmasked_pix = self.set_column_properties("SHE_STARCAT_STAR_UNMASKED_PIX", dtype=">i4",
                                                            fits_dtype="J",
                                                            comment="Total number of unmasked pixels covered by "
                                                                    "this star.")

        self.rr_dist = self.set_column_properties("SHE_STARCAT_RR_DIST", dtype=">f4", fits_dtype="E",
                                                  is_optional=True, comment="Distance from readout register - "
                                                                            "only used internally within CTI-PSF "
                                                                            "Validation test.")

        self._finalize_init()


# Define an instance of this object that can be imported
SHE_STAR_CAT_TF = SheStarCatalogFormat()

# And a convenient alias for it
TF = SHE_STAR_CAT_TF
