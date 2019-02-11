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

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import is_in_format
import numpy as np


logger = getLogger(mv.logger_name)


class PsfTmStateTableMeta(object):
    """ A class defining the metadata for PSF TM state tables.
    """

    def __init__(self):

        self.__version__ = "0.1"
        self.table_format = "she.PsfTmStateTable"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.extname = mv.extname_label
        
        self.identity = mv.psf_state_identity_label

        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.extname, None),
                                     (self.identity, "Zernike-mode fit or Telescope Model fit"),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class PsfTmStateTableFormat(object):
    """
        @brief A class defining the format for PSF TM state tables. Only the psf_tm_state_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
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

        for colname in ["M1TRAD", "M2TRAD", "FOM1TFRN", "FOM2TFRN",
                        "M3TRAD", "DicTFRN", "M1TCON", "M2TCON",
                        "M3TCON", "M2TZ", "M2TX", "M2TY",
                        "M2RX", "M2RY", "M3TZ", "M3TX",
                        "M3TY", "M3RX", "M3RY"]:
            setattr(self,colname.lower(),set_column_properties(name=colname))

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)

# Define an instance of this object that can be imported
psf_table_format = PsfTmStateTableFormat()

# And a convient alias for it
tf = psf_table_format


def make_psf_tm_state_table_header(model_hash=None,
                                   model_seed=None,
                                   noise_seed=None):
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

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    header[tf.m.extname] = mv.psf_tm_state_tag

    header[tf.m.identity] = mv.psf_tm_identity

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    return header


def initialise_psf_tm_state_table(model_hash=None,
                                  model_seed=None,
                                  noise_seed=None,
                                  optional_columns=None,
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
