""" @file star_catalog.py

    Created 23 July 2018

    Format definition for a table containing Star Catalog data.
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


from collections import OrderedDict

from SHE_PPT.constants.fits import OBS_ID_LABEL, OBS_TIME_LABEL

from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL
from ..table_utility import is_in_format, init_table, SheTableFormat
fits_version = "8.0"
fits_def = "she.starCatalog"


class SheStarCatalogMeta():
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = FITS_VERSION_LABEL
        self.fits_def = FITS_DEF_LABEL

        self.roll_ang = "ROLLANGL"
        self.exposure_product_id = "EXP_PID"
        self.observation_id = OBS_ID_LABEL
        self.observation_time = OBS_TIME_LABEL

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.roll_ang, None),
                                     (self.exposure_product_id, None),
                                     (self.observation_id, None),
                                     (self.observation_time, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheStarCatalogFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the star_catalog_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheStarCatalogMeta())

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

        self._finalize_init()


# Define an instance of this object that can be imported
star_catalog_format = SheStarCatalogFormat()

# And a convient alias for it
tf = star_catalog_format


def make_star_catalog_header(roll_ang, exposure_product_id, observation_id, observation_time):
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def
    header[tf.m.roll_ang] = roll_ang
    header[tf.m.exposure_product_id] = exposure_product_id
    header[tf.m.observation_id] = observation_id
    header[tf.m.observation_time] = observation_time
    return header


def initialise_star_catalog(roll_ang=None,
                            exposure_product_id=None,
                            observation_id=None,
                            observation_time=None,
                            size=None,
                            optional_columns=None,
                            init_cols=None,):
    """
        @brief Initialise a galaxy population table.

        @return star_catalog <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    star_catalog = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    star_catalog.meta = make_star_catalog_header(
        roll_ang, exposure_product_id, observation_id, observation_time)

    assert is_in_format(star_catalog, tf)

    return star_catalog
