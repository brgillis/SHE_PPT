""" @file p_of_e.py

    Created 10 Oct 2017

    Format definition for galaxy population table.
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


from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL, EXTNAME_LABEL
from ..table_utility import is_in_format, init_table, SheTableFormat


fits_version = "8.0"
fits_def = "she.pOfE"


class ShePOfEMeta():
    """
        @brief A class defining the metadata for PSF tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = FITS_VERSION_LABEL
        self.fits_def = FITS_DEF_LABEL

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class ShePOfEFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the p_of_e_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(ShePOfEMeta())

        # Column names and info

        self.ID = self.set_column_properties(
                                        "ID", dtype=">i8", fits_dtype="K",
                                        comment="Link to galaxy population table.")

        self.e1 = self.set_column_properties(
                                        "E1", comment="Using flat weight function.")
        self.e2 = self.set_column_properties(
                                        "E2", comment="Using flat weight function.")

        self.bulge_e1 = self.set_column_properties("BULGE_E1", is_optional=True)
        self.bulge_e2 = self.set_column_properties("BULGE_E2", is_optional=True)

        self.disk_e1 = self.set_column_properties("DISK_E1", is_optional=True)
        self.disk_e2 = self.set_column_properties("DISK_E2", is_optional=True)

        self._finalize_init()


# Define an instance of this object that can be imported
p_of_e_table_format = ShePOfEFormat()

# And a convient alias for it
tf = p_of_e_table_format


def make_p_of_e_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    return header


def initialise_p_of_e_table(size=None,
                            optional_columns=None,
                            init_cols=None,):
    """
        @brief Initialise a galaxy population table.

        @return p_of_e_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    p_of_e_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    p_of_e_table.meta = make_p_of_e_table_header()

    assert is_in_format(p_of_e_table, tf)

    return p_of_e_table
