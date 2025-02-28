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

__updated__ = "2021-08-12"

from ..constants.fits import FITS_DEF_LABEL, FITS_VERSION_LABEL
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.pOfE"


class ShePOfEMeta(SheTableMeta):
    """
        @brief A class defining the metadata for PSF tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL


class ShePOfEFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the p_of_e_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = ShePOfEMeta

    def __init__(self):
        super().__init__()

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

# And a convenient alias for it
tf = p_of_e_table_format
