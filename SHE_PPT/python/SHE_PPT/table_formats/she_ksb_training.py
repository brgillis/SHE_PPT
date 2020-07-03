""" @file she_ksb_training.py

    Created 23 July 2018

    Format definition for a table containing KSB training data.
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
from SHE_PPT.table_formats.she_training import SheTrainingMeta, SheTrainingFormat
from SHE_PPT.table_utility import is_in_format

fits_version = "8.0"
fits_def = "she.ksbTraining"

child_label = "SHE_KSB_TRAINING_"


class SheKsbTrainingMeta(SheTrainingMeta):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        # Inherit meta format from parent class
        super().__init__()

        self.__version__ = fits_version
        self.table_format = fits_def

        return


class SheKsbTrainingFormat(SheTrainingFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the ksb_training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__()

        # Get the metadata (contained within its own class)
        self.meta = SheKsbTrainingMeta()

        # And a quick alias for it
        self.m = self.meta

        # Get the version from the meta class
        self.__version__ = self.m.__version__
        self.child_label = child_label

        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all

        self.is_base = False

        self.parent_is_optional = self.is_optional
        self.parent_comments = self.comments
        self.parent_dtypes = self.dtypes
        self.parent_fits_dtypes = self.fits_dtypes
        self.parent_lengths = self.lengths
        self.parent_all = self.all
        self.parent_all_required = self.all_required

        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        changed_column_names = {}

        for parent_name in self.parent_all:
            if parent_name == "OBJECT_ID":
                name = parent_name
            else:
                name = child_label + parent_name
                changed_column_names[parent_name] = name

            self.is_optional[name] = self.parent_is_optional[parent_name]
            self.comments[name] = self.parent_comments[parent_name]
            self.dtypes[name] = self.parent_dtypes[parent_name]
            self.fits_dtypes[name] = self.parent_fits_dtypes[parent_name]
            self.lengths[name] = self.parent_lengths[parent_name]

        # Update existing column names inherited from parent
        for key, val in tuple(zip(self.__dict__.items()))[0]:
            print(str(val))
            if val in changed_column_names:
                setattr(self, key, changed_column_names[val])

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
ksb_training_table_format = SheKsbTrainingFormat()

# And a convient alias for it
tf = ksb_training_table_format


def make_ksb_training_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    return header


def initialise_ksb_training_table(optional_columns=None):
    """
        @brief Initialise a galaxy population table.

        @return ksb_training_table <astropy.Table>
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

    ksb_training_table = Table(init_cols, names=names, dtype=dtypes)

    ksb_training_table.meta = make_ksb_training_table_header()

    assert(is_in_format(ksb_training_table, tf))

    return ksb_training_table
