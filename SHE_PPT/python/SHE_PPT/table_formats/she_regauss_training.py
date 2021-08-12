""" @file regauss_training.py

    Created 23 July 2018

    Format definition for a table containing REGAUSS training data.
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

__updated__ = "2021-08-12"

from collections import OrderedDict

from ..table_formats.she_training import SheTrainingMeta, SheTrainingFormat
from ..table_utility import is_in_format, init_table


fits_version = "8.0"
fits_def = "she.regaussTraining"

child_label = "SHE_REGAUSS_TRAINING_"


class SheRegaussTrainingMeta(SheTrainingMeta):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def


class SheRegaussTrainingFormat(SheTrainingFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the regauss_training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__(SheRegaussTrainingMeta(), finalize=False)

        self.setup_child_table_format(child_label)

        self._finalize_init()


# Define an instance of this object that can be imported
regauss_training_table_format = SheRegaussTrainingFormat()

# And a convient alias for it
tf = regauss_training_table_format


def make_regauss_training_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    return header


def initialise_regauss_training_table(size=None,
                                      optional_columns=None,
                                      init_cols=None,):
    """
        @brief Initialise a galaxy population table.

        @return regauss_training_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    regauss_training_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    regauss_training_table.meta = make_regauss_training_table_header()

    assert is_in_format(regauss_training_table, tf)

    return regauss_training_table
