""" @file psf_state.py

    Created 11 Feb 2019

    Base class for format definitions for PSF states.
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

from typing import List, Optional, Type

from ..constants.fits import (EXTNAME_LABEL, FITS_DEF_LABEL, FITS_VERSION_LABEL, PSF_CALIB_PARAM_DEF,
                              PSF_FIELD_PARAM_DEF, )
from ..logging import getLogger
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"

logger = getLogger(__name__)


class ShePsfStateMeta(SheTableMeta):
    """ A class defining the metadata for PSF TM state tables.
    """

    __version__: str = fits_version

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL

    extname: str = EXTNAME_LABEL

    # Table info
    _data_type: str = "CAL"
    _main_data_type: str
    _identity: str
    _format: str

    def __init__(self, data_type = "CAL", **kwargs):
        self._data_type = data_type

        self._main_data_type = (PSF_FIELD_PARAM_DEF
                                if self._data_type == "FIELD" else
                                PSF_CALIB_PARAM_DEF)
        self.table_format = f"{self._main_data_type}.{self._format}"

        super().__init__(**kwargs)


class ShePsfStateFormat(SheTableFormat):

    _data_type: str = "CAL"
    _meta_type: Type
    _l_colnames: Optional[List[str]] = None

    def __init__(self,
                 data_type = "CAL"):
        super().__init__(self._meta_type(data_type))

        # Get the metadata (contained within its own class)

        self._data_type = data_type

        # Column names and info

        if not self._l_colnames:
            self._l_colnames = []

        for colname in self._l_colnames:
            setattr(self, colname.lower(),
                    self.set_column_properties(name=self.get_colname(colname),
                                               dtype=">f4", fits_dtype="E"))

        self._finalize_init()

    def get_colname(self, colname):
        """ Get full column name
        """
        return f"SHE_PSF_{self._data_type}_{colname}"
