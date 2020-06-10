""" @file psf_tm_state.py

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

__updated__ = "2019-02-27"

from collections import OrderedDict

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table
import numpy as np


logger = getLogger(mv.logger_name)


class PsfTmStateTableMeta(object):
    """ A class defining the metadata for PSF TM state tables.
    """

    data_type = "FIELD"
    
    def __init__(self):

        self.__version__ = "8.0"
        
        self.main_data_type = ("she.psfFieldParameters" 
                               if self.data_type=="FIELD" else 
                               "she.psfCalibrationParameters")
        self.table_format = "%s.SheTelescopeModeParams" % self.main_data_type

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.extname = mv.extname_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class PsfTmStateTableFormat(object):
    """
        @brief A class defining the format for PSF TM state tables. Only the psf_tm_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self, data_type="FIELD"):

        # Get the metadata (contained within its own class)
        
        self.data_type = data_type

        self.meta = PsfTmStateTableMeta()

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
        # @TODO: option for FIELD/CALIB - use self.data_type
        


        for colname in ["M1TRAD", "M2TRAD", "FOM1TFRN", "FOM2TFRN",
                        "M3TRAD", "DIC_TFRN", "M1TCON", "M2TZ",
                        "M2TX", "M2TY", "M2RX", "M2RY", "M3TZ", "M3TX",
                        "M3TY", "M3RX", "M3RY"]:
            setattr(self, colname.lower(), 
                    set_column_properties(name=self.get_colname(colname),
                        dtype=">f4", fits_dtype="E"))

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

    def get_colname(self, colname):
        """ Get full column name
        """
        return "SHE_PSF_%s_%s" % (self.data_type,colname)
        
# Define an instance of this object that can be imported
psf_table_format_field = PsfTmStateTableFormat("FIELD")
psf_table_format_calib = PsfTmStateTableFormat("CAL")

# And a convenient alias for it
# Can define multiple aliases if slightly different types

tff = psf_table_format_field
tfc = psf_table_format_calib

def make_psf_tm_state_table_header(data_type="FIELD"):
    """Generate a header for a PSF TM State table.

    Parameters
    ----------
    model_hash : str
        Hash of the physical model options dictionary, if applicable
    model_seed : int
        Full seed used for the physical model for this image, if applicable
    noise_seed : int
        Seed used for generating noise for this image, if applicable

    Return
    ------
    header : OrderedDict
    """

    if data_type=="FIELD":
        tf=tff
    else:
        tf=tfc

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    
    return header


def initialise_psf_tm_state_table(data_type="FIELD",optional_columns=None,
                                  init_columns={}):
    """Initialise a PSF TM State table.

    Parameters
    ----------
    model_hash : str
        Hash of the physical model options dictionary, if applicable
    model_seed : int
        Full seed used for the physical model for this image, if applicable
    noise_seed : int
        Seed used for generating noise for this image, if applicable
    optional_columns : <list<str>>
        List of names for optional columns to include.
    init_columns : dict<str:array>
        Dictionary of columns to initialise the table with

    Return
    ------
    psf_tm_state_table : astropy.Table
    """

    if data_type=="FIELD":
        tf=tff
    else:
        tf=tfc

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

    psf_tm_state_table = Table(init_cols, names=names, dtype=dtypes)

    psf_tm_state_table.meta = make_psf_tm_state_table_header(model_hash=model_hash,
                                                             model_seed=model_seed,
                                                             noise_seed=noise_seed)

    assert(is_in_format(psf_tm_state_table, tf))

    return psf_tm_state_table
