""" @file psf_om_state.py

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
from typing import Type

from ..constants.fits import PSF_OM_IDENTITY, PSF_OM_STATE_TAG
from ..logging import getLogger
from ..table_formats.she_psf_state import ShePsfStateFormat, ShePsfStateMeta

fits_version = "8.0"

logger = getLogger(__name__)


class ShePsfOmStateMeta(ShePsfStateMeta):
    """ A class defining the metadata for PSF OM state tables.
    """

    __version__: str = fits_version
    _identity: str = PSF_OM_IDENTITY
    _format: str = "SheOtherModelParams"

    def init_meta(self,
                  **kwargs: str) -> OrderedDict:
        return super().init_meta(extname=PSF_OM_STATE_TAG,
                                 **kwargs)


class ShePsfOmStateFormat(ShePsfStateFormat):
    """
        @brief A class defining the format for PSF OM state tables. Only the psf_om_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    _data_type: str = "CAL"
    _meta_type: Type = ShePsfOmStateMeta


# Define an instance of this object that can be imported
psf_table_format_field = ShePsfOmStateFormat("FIELD")
psf_table_format_calib = ShePsfOmStateFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib
