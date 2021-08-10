""" @file psf_dm_state.py

    Created 11 Feb 2019

    Format definition for PSF Zernike Mode state table. This is based on Chris's description in the DPDD and
    implementation in his code.
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

__updated__ = "2020-07-19"

from collections import OrderedDict

from .. import magic_values as mv
from ..logging import getLogger
from ..table_utility import is_in_format, init_table,SheTableFormat


fits_version = "8.0"

logger = getLogger(mv.logger_name)


class ShePsfDmStateMeta():
    """ A class defining the metadata for PSF TM state tables.
    """

    data_type = "CAL"

    def __init__(self, data_type):

        self.data_type = data_type
        self.__version__ = fits_version

        self.main_data_type = (mv.psf_field_param_def
                               if self.data_type == "FIELD" else
                               mv.psf_calib_param_def)
        self.table_format = "%s.SheDetectorModelParams" % self.main_data_type
        self.identity = mv.psf_dm_identity

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.extname = mv.extname_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.extname, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class ShePsfDmStateFormat(SheTableFormat):
    """
        @brief A class defining the format for PSF TM state tables. Only the psf_dm_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    data_type = "CAL"

    def __init__(self, data_type="CAL"):
        super().__init__(ShePsfDmStateMeta(data_type))

        # Get the metadata (contained within its own class)

        self.data_type = data_type

        # Column names and info
        # @TODO: option for FIELD/CALIB - use self.data_type

        for colname in []:
            setattr(self, colname.lower(),
                    self.set_column_properties(name=self.get_colname(colname),
                                          dtype=">f4", fits_dtype="E"))

        self._finalize_init()

    def get_colname(self, colname):
        """ Get full column name
        """
        return "SHE_PSF_%s_%s" % (self.data_type, colname)


# Define an instance of this object that can be imported
psf_table_format_field = ShePsfDmStateFormat("FIELD")
psf_table_format_calib = ShePsfDmStateFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib


def make_psf_dm_state_table_header(data_type="FIELD"):
    """Generate a header for a PSF DM State table.

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
    header[tf.m.extname] = mv.psf_dm_state_tag

    return header


def initialise_psf_dm_state_table(data_type="FIELD", size=None,
                                  optional_columns=None,
                                  init_cols=None,
                                  init_columns={}):
    """Initialise a PSF TM State table.

    Parameters
    ----------
    data_type : str
        Is it FIELD or CALIB
    optional_columns : <list<str>>
        List of names for optional columns to include.
    init_columns : dict<str:array>
        Dictionary of columns to initialise the table with

    Return
    ------
    psf_dm_state_table : astropy.Table
    """

    tf = tff if data_type == "FIELD" else tfc

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    psf_dm_state_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    psf_dm_state_table.meta = make_psf_dm_state_table_header(data_type)

    assert is_in_format(psf_dm_state_table, tf)

    return psf_dm_state_table

# Initialisers for field/calibration variants


def initialise_psf_field_dm_state_table(size=None,
                                        optional_columns=None,
                                        init_cols=None,
                                        init_columns=None):

    if init_columns is None:
        init_columns = {}
    return initialise_psf_dm_state_table(data_type="FIELD", optional_columns=optional_columns,
                                         init_columns=init_columns)


def initialise_psf_calibration_dm_state_table(size=None,
                                              optional_columns=None,
                                              init_cols=None,
                                              init_columns=None):

    if init_columns is None:
        init_columns = {}
    return initialise_psf_dm_state_table(data_type="CALIB", optional_columns=optional_columns,
                                         init_columns=init_columns)
