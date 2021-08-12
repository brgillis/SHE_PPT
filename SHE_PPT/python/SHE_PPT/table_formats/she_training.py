""" @file she_training.py

    Created 23 July 2018

    Base format definition for a table containing generic training data.
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

__updated__ = "2021-08-10"

from collections import OrderedDict


from ..constants.fits import fits_version_label, fits_def_label, extname_label
from ..table_utility import SheTableFormat


fits_version = "8.0"
fits_def = "she.training"


class SheTrainingMeta():
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheTrainingFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self, meta=None, finalize: bool = True):
        if meta is None:
            meta = SheTrainingMeta()
        super().__init__(meta)

        # Column names and info

        self.id = self.set_column_properties("OBJECT_ID", dtype=">i8", fits_dtype="K",
                                             comment="ID of this object in the galaxy population priors table.")
        self.e1 = self.set_column_properties("E1", dtype=">f4", fits_dtype="E",
                                             comment="Mean ellipticity measurement of this object, component 1")
        self.e2 = self.set_column_properties("E2", dtype=">f4", fits_dtype="E",
                                             comment="Mean ellipticity measurement of this object, component 2")
        self.e1_err = self.set_column_properties("E1_ERR", dtype=">f4", fits_dtype="E",
                                                 comment="Error on mean ellipticity measurement of this object, component 1")
        self.e2_err = self.set_column_properties("E2_ERR", dtype=">f4", fits_dtype="E",
                                                 comment="Error on mean ellipticity measurement of this object, component 2")

        if finalize:
            self._finalize_init()


# Define an instance of this object that can be imported
training_table_format = SheTrainingFormat()

# And a convient alias for it
tf = training_table_format
