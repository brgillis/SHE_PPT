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

__updated__ = "2020-07-03"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.table_utility import setup_table_format, set_column_properties

fits_version = "8.0"
fits_def = "she.ksbMeasurements"


class SheTrainingMeta(object):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheTrainingFormat(object):
    """
        @brief A class defining the format for galaxy population priors tables. Only the training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = SheTrainingMeta()

        setup_table_format(self)

        # Column names and info

        self.id = set_column_properties(self, "OBJECT_ID", dtype=">i8", fits_dtype="K",
                                        comment="ID of this object in the galaxy population priors table.")
        self.e1 = set_column_properties(self, "TRAINING_E1", dtype=">f4", fits_dtype="E",
                                        comment="Mean ellipticity measurement of this object, component 1")
        self.e2 = set_column_properties(self, "TRAINING_E2", dtype=">f4", fits_dtype="E",
                                        comment="Mean ellipticity measurement of this object, component 2")
        self.e1_err = set_column_properties(self, "TRAINING_E1_ERR", dtype=">f4", fits_dtype="E",
                                        comment="Error on mean ellipticity measurement of this object, component 1")
        self.e2_err = set_column_properties(self, "TRAINING_E2_ERR", dtype=">f4", fits_dtype="E",
                                        comment="Error on mean ellipticity measurement of this object, component 2")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
training_table_format = SheTrainingFormat()

# And a convient alias for it
tf = training_table_format
