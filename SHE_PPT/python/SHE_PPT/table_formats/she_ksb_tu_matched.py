""" @file ksb_tu_matched.py

    Created 2021/08/10

    Format definition for ksb tu_matched tables.
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

from ..logging import getLogger
from ..table_formats.she_tu_matched import SheTUMatchedMeta, SheTUMatchedFormat

fits_version = "8.0"
fits_def = "she.ksbTUMatched"

child_label = "SHE_KSB_"

logger = getLogger(__name__)


class SheKsbTUMatchedMeta(SheTUMatchedMeta):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def


class SheKsbTUMatchedFormat(SheTUMatchedFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the ksb_tu_matched_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__(SheKsbTUMatchedMeta(), finalize = False)

        self.setup_child_table_format(child_label)

        # ksb specific columns

        self._finalize_init()


# Define an instance of this object that can be imported
ksb_tu_matched_table_format = SheKsbTUMatchedFormat()

# And a convenient alias for it
tf = ksb_tu_matched_table_format
