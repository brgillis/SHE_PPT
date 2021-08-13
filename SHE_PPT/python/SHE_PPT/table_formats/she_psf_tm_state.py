""" @file psf_tm_state.py

    Created 11 Feb 2019

    Format definition for PSF Zernike Mode state table. This is based on Chris's description in the DPDD and
    implementation in his code.
"""

__updated__ = "2021-08-13"

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

from collections import OrderedDict
from typing import Optional, List, Type

from ..constants.fits import PSF_TM_STATE_TAG, PSF_TM_IDENTITY
from ..logging import getLogger
from ..table_formats.she_psf_state import ShePsfStateFormat, ShePsfStateMeta


fits_version = "8.0"

logger = getLogger(__name__)


class ShePsfTmStateMeta(ShePsfStateMeta):
    """ A class defining the metadata for PSF TM state tables.
    """

    __version__: str = fits_version
    _identity: str = PSF_TM_IDENTITY
    _format: str = "SheTelescopeModeParams"

    def init_meta(self,
                  **kwargs: str) -> OrderedDict:
        return super().init_meta(extname=PSF_TM_STATE_TAG,
                                 **kwargs)


class ShePsfTmStateFormat(ShePsfStateFormat):
    """
        @brief A class defining the format for PSF TM state tables. Only the psf_tm_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    _data_type: str = "CAL"
    _meta_type: Type = ShePsfTmStateMeta
    _l_colnames: Optional[List[str]] = ["M1TRAD", "M2TRAD", "FOM1TFRN", "FOM2TFRN",
                                        "M3TRAD", "DIC_TFRN", "M1TCON", "M2TCON",
                                        "M3TCON", "M2TZ", "M2TX", "M2TY", "M2RX",
                                        "M2RY", "M3TZ", "M3TX", "M3TY", "M3RX", "M3RY"]


# Define an instance of this object that can be imported
psf_table_format_field = ShePsfTmStateFormat("FIELD")
psf_table_format_calib = ShePsfTmStateFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib
