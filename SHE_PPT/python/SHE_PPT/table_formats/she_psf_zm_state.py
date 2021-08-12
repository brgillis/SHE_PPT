""" @file psf_zm_state.py

    Created 11 Feb 2019

    Format definition for PSF Zernike Mode state table. This is based on Chris's description in the DPDD and
    implementation in his code.
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

from collections import OrderedDict

from ..constants.fits import (fits_version_label, fits_def_label, extname_label,
                              psf_field_param_def, psf_calib_param_def, psf_zm_state_tag)
from ..constants.tables import psf_zm_identity
from ..logging import getLogger
from ..table_utility import is_in_format, init_table, SheTableFormat


fits_version = "8.0"

logger = getLogger(__name__)


class ShePsfZmStateMeta():
    """ A class defining the metadata for PSF ZM state tables.
    """

    data_type = "FIELD"

    def __init__(self, data_type):

        self.data_type = data_type
        self.__version__ = fits_version

        self.main_data_type = (psf_field_param_def
                               if self.data_type == "FIELD" else
                               psf_calib_param_def)
        self.table_format = "%s.SheZernikeModeParams" % self.main_data_type
        self.identity = psf_zm_identity

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label

        self.extname = extname_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.extname, None),
                                     ))

        # A list of headers in the desired order
        self.all = list(self.comments.keys())


class ShePsfZmStateFormat(SheTableFormat):
    """
        @brief A class defining the format for PSF ZM state tables. Only the psf_zm_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    data_type = "FIELD"

    def __init__(self, data_type="FIELD"):
        super().__init__(ShePsfZmStateMeta(self.data_type))

        self.data_type = data_type

        # Column names and info

        self.fovrngx = self.set_column_properties(
            "SHE_PSF_%s_FOVRNGX" % self.data_type, dtype=">f4",
            fits_dtype="E", length=2)
        self.fovrngy = self.set_column_properties(
            "SHE_PSF_%s_FOVRNGY" % self.data_type, dtype=">f4",
            fits_dtype="E", length=2)
        self.zer_ply_amp = self.set_column_properties(
            "SHE_PSF_%s_ZNKPLYAMP" % self.data_type, dtype=">f4",
            fits_dtype="E", length=50)

        self._finalize_init()


# Define an instance of this object that can be imported
psf_table_format_field = ShePsfZmStateFormat("FIELD")
psf_table_format_calib = ShePsfZmStateFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib


def make_psf_zm_state_table_header(data_type="FIELD"):
    """Generate a header for a PSF ZM State table.

    Parameters
    ----------
    data_type : Is it field or calibration

    Return
    ------
    header : OrderedDict
    """

    tf = tff if data_type == "FIELD" else tfc

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = tf.m.table_format
    header[tf.m.extname] = psf_zm_state_tag

    return header


def initialise_psf_zm_state_table(data_type="FIELD",
                                  size=None,
                                  optional_columns=None,
                                  init_cols=None,
                                  init_columns={}):
    """Initialise a PSF ZM State table.

    Parameters
    ----------
    data_type : str
        Is if FIELD or CALIB
    optional_columns : <list<str>>
        List of names for optional columns to include.
    init_columns : dict<str:array>
        Dictionary of columns to initialise the table with

    Return
    ------
    psf_zm_state_table : astropy.Table
    """

    tf = tff if data_type == "FIELD" else tfc

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    psf_zm_state_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    psf_zm_state_table.meta = make_psf_zm_state_table_header(data_type)

    assert is_in_format(psf_zm_state_table, tf)

    return psf_zm_state_table

# Initialisers for field/calibration variants


def initialise_psf_field_zm_state_table(size=None,
                                        optional_columns=None,
                                        init_cols=None,
                                        init_columns=None):

    if init_columns is None:
        init_columns = {}
    return initialise_psf_zm_state_table(data_type="FIELD", optional_columns=optional_columns,
                                         init_columns=init_columns)


def initialise_psf_calibration_zm_state_table(size=None,
                                              optional_columns=None,
                                              init_cols=None,
                                              init_columns=None):

    if init_columns is None:
        init_columns = {}
    return initialise_psf_zm_state_table(data_type="CALIB", optional_columns=optional_columns,
                                         init_columns=init_columns)
