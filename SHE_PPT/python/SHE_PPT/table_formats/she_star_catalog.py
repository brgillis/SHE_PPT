""" @file star_catalog.py

    Created 23 July 2018

    Format definition for a table containing Star Catalog data.
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

__updated__ = "2020-06-24"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.table_utility import is_in_format

fits_version = "8.0"
fits_def = "she.starCatalog"


class StarCatalogTableMeta(object):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.roll_ang = "ROLLANGL"
        self.exposure_product_id = "EXP_PID"
        self.observation_id = mv.obs_id_label
        self.observation_time = mv.obs_time_label

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


class StarCatalogTableFormat(object):
    """
        @brief A class defining the format for galaxy population priors tables. Only the star_catalog_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = StarCatalogTableMeta()

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

        self.id = set_column_properties(
            "OBJECT_ID", dtype=">i8", fits_dtype="K",
            comment="ID of this object in the galaxy population priors table.")

        self.det_x = set_column_properties(
            "SHE_STARCAT_DET_X", dtype=">i4", fits_dtype="I")
        self.det_y = set_column_properties(
            "SHE_STARCAT_DET_Y", dtype=">i4", fits_dtype="I")
        self.x = set_column_properties(
            "SHE_STARCAT_X", dtype=">f4", fits_dtype="E")
        self.x_err = set_column_properties(
            "SHE_STARCAT_X_ERR", dtype=">f4", fits_dtype="E")
        self.y = set_column_properties(
            "SHE_STARCAT_Y", dtype=">f4", fits_dtype="E")
        self.y_err = set_column_properties(
            "SHE_STARCAT_Y_ERR", dtype=">f4", fits_dtype="E")
        self.ra = set_column_properties(
            "SHE_STARCAT_UPDATED_RA", comment="deg", dtype=">f8", fits_dtype="D")
        self.ra_err = set_column_properties(
            "SHE_STARCAT_UPDATED_RA_ERR", comment="deg", dtype=">f8", fits_dtype="E")
        self.dec = set_column_properties(
            "SHE_STARCAT_UPDATED_DEC", comment="deg", dtype=">f8", fits_dtype="D")
        self.dec_err = set_column_properties(
            "SHE_STARCAT_UPDATED_DEC_ERR", comment="deg", dtype=">f8", fits_dtype="E")
        self.flux = set_column_properties(
            "SHE_STARCAT_FLUX", dtype=">f4", fits_dtype="E")
        self.flux_err = set_column_properties(
            "SHE_STARCAT_FLUX_ERR", dtype=">f4", fits_dtype="E")

        self.e1 = set_column_properties("SHE_STARCAT_E1", dtype=">f4", fits_dtype="E",
                                        comment="Mean ellipticity measurement of this object, component 1")
        self.e2 = set_column_properties("SHE_STARCAT_E2", dtype=">f4", fits_dtype="E",
                                        comment="Mean ellipticity measurement of this object, component 2")
        self.e1_err = set_column_properties("SHE_STARCAT_E1_ERR", dtype=">f4", fits_dtype="E",
                                        comment="Error on mean ellipticity measurement of this object, component 1")
        self.e2_err = set_column_properties("SHE_STARCAT_E2_ERR", dtype=">f4", fits_dtype="E",
                                        comment="Error on mean ellipticity measurement of this object, component 2")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
star_catalog_table_format = StarCatalogTableFormat()

# And a convient alias for it
tf = star_catalog_table_format


def make_star_catalog_table_header(roll_ang, exposure_product_id, observation_id, observation_time):
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


def initialise_star_catalog_table(roll_ang, exposure_product_id, observation_id, observation_time,
                                  optional_columns=None):
    """
        @brief Initialise a galaxy population table.

        @return star_catalog_table <astropy.Table>
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

    star_catalog_table = Table(init_cols, names=names, dtype=dtypes)

    star_catalog_table.meta = make_star_catalog_table_header(
        roll_ang, exposure_product_id, observation_id, observation_time)

    assert(is_in_format(star_catalog_table, tf))

    return star_catalog_table
