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

__updated__ = "2021-08-12"

from ..table_formats.she_training import SheTrainingMeta, SheTrainingFormat


fits_version = "8.0"
fits_def = "she.ksbTraining"

child_label = "SHE_KSB_TRAINING_"


class SheKsbTrainingMeta(SheTrainingMeta):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def


class SheKsbTrainingFormat(SheTrainingFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the ksb_training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__(meta=SheKsbTrainingMeta(), finalize=False)

        self.setup_child_table_format(child_label)

        self._finalize_init()


# Define an instance of this object that can be imported
ksb_training_table_format = SheKsbTrainingFormat()

# And a convient alias for it
tf = ksb_training_table_format
