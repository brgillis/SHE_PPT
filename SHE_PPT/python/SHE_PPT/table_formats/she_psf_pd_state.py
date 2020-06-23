""" @file psf_pd_state.py

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

__updated__ = "2020-06-23"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
import numpy as np

fits_version = "8.0"

logger = getLogger(mv.logger_name)


class PsfPdStateTableMeta(object):
    """ A class defining the metadata for PSF ZM state tables.
    """

    data_type = "FIELD"

    def __init__(self, data_type):

        self.data_type = data_type
        self.__version__ = fits_version

        self.main_data_type = (mv.psf_field_param_def
                               if self.data_type == "FIELD" else
                               mv.psf_calib_param_def)
        self.table_format = "%s.ShePsfDiagnostics" % self.main_data_type

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label

        self.extname = mv.extname_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class PsfPdStateTableFormat(object):
    """
        @brief A class defining the format for PSF ZM state tables. Only the psf_pd_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    data_type = "FIELD"

    def __init__(self, data_type="FIELD"):

        self.data_type = data_type
        # Get the metadata (contained within its own class)
        self.meta = PsfPdStateTableMeta(self.data_type)

        # And a quick alias for it
        self.m = self.meta

        # Get the version from the meta class
        self.__version__ = self.m.__version__

        # Direct alias for a tuple of all metadata
        self.meta_data = self.m.all

        # Dicts for less-used properties
        self.is_optional = OrderedDict()
        self.comments = OrderedDict()
        self.dtypes = OrderedDict()
        self.fits_dtypes = OrderedDict()
        self.lengths = OrderedDict()

        def set_column_properties(name, is_optional=False, comment=None, dtype=">f4", fits_dtype="E",
                                  length=1):

            assert name not in self.is_optional

            self.is_optional[name] = is_optional
            self.comments[name] = comment
            self.dtypes[name] = dtype
            self.fits_dtypes[name] = fits_dtype
            self.lengths[name] = length

            return name

        # Column names and info

        self.id = set_column_properties(
            "OBJECT_ID", dtype=">i8", fits_dtype="K")
        self.chisq = set_column_properties(
            "SHE_PSF_%s_CHISQ" % self.data_type, dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
psf_table_format_field = PsfPdStateTableFormat("FIELD")
psf_table_format_calib = PsfPdStateTableFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib


def make_psf_pd_state_table_header(data_type="FIELD"):
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
    header[tf.m.fits_def] = fits_def

    header[tf.m.extname] = mv.psf_pd_state_tag

    header[tf.m.identity] = mv.psf_pd_identity

    return header


def initialise_psf_pd_state_table(data_type="FIELD",
                                  optional_columns=None,
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
    psf_pd_state_table : astropy.Table
    """

    tf = tff if data_type == "FIELD" else tfc

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

            dtype = (tf.dtypes[colname], tf.lengths[colname])

            if colname in init_columns:
                init_cols.append(init_columns[colname])
            elif len(init_columns) > 0:
                init_cols.append(
                    np.zeros(len(init_columns.values[0]), dtype=dtype))
            else:
                init_cols.append([])

            dtypes.append(dtype)

    psf_pd_state_table = Table(init_cols, names=names, dtype=dtypes)

    psf_pd_state_table.meta = make_psf_pd_state_table_header(data_type)

    assert(is_in_format(psf_pd_state_table, tf))

    return psf_pd_state_table
