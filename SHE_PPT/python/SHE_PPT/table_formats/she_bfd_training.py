""" @file bfd_training.py

    Created 23 July 2018

    Format definition for a table containing BFD training data.
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

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.mer_final_catalog import tf as detf
from SHE_PPT.table_utility import is_in_format
from astropy.table import Table

class KsbTrainingTableMeta(object):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = "8.0"
        self.table_format = "she.KsbTrainingTable"

        # Table metadata labels
        self.version = "SS_VER"
        self.format = "SS_FMT"

        self.sflagvers="SFLAGVERS"
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        self.obs_id = 0
        self.date_obs = mv.obs_time_label
        self.tile_id = 0
        self.nlost = "NLOST"
        self.wt_n = "WT_N"
        self.wt_sigma = "WT_SIGMA"
        self.bfd_tmpl_snmin = "T_SNMIN"
        self.bfd_tmpl_sigma_xy = "T_SIGXY"
        self.bfd_tmpl_sigma_flux = "T_SIGFLX"
        self.bfd_tmpl_sigma_step = "T_SIGSTP"
        self.bfd_tmpl_sigma_max = "T_SIGMAX"
        self.bfd_tmpl_xy_max = "T_XYMAX"
        self.validated = "VALID"
        
        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.version, None),
                                     (self.format, None),
                                     (self.sflagvers,None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.obs_id,None),
                                     (self.date_obs, None),
                                     (self.tile_id, None),
                                     (self.nlost, None),
                                     (self.wt_n, None),
                                     (self.wt_sigma, None),
                                     (self.bfd_tmpl_snmin, None),
                                     (self.bfd_tmpl_sigma_xy, None),
                                     (self.bfd_tmpl_sigma_flux, None),
                                     (self.bfd_tmpl_sigma_step, None),
                                     (self.bfd_tmpl_sigma_max, None),
                                     (self.bfd_tmpl_xy_max, None),
                                     (self.validated,
                                      "0: Not tested; 1: Pass; -1: Fail")))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class KsbTrainingTableFormat(object):
    """
        @brief A class defining the format for galaxy population priors tables. Only the bfd_training_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = KsbTrainingTableMeta()

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
            "OBJECT_ID", dtype=">i8", fits_dtype="K",
            comment="ID of this object in the galaxy population priors table.")
        self.fit_flags = set_column_properties(
            "SHE_BFD_TRAINING_FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = set_column_properties(
            "SHE_BFD_TRAINING_VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties(
            "SHE_BFD_TRAINING_FIT_CLASS", dtype=">i4", fits_dtype="I")
        self.ra = set_column_properties(
            "SHE_BFD_TRAINING_UPDATED_RA", comment="deg", dtype=">f8", fits_dtype="D")
        self.ra_err = set_column_properties(
            "SHE_BFD_TRAINING_UPDATED_RA_ERR", comment="deg", dtype=">f8", fits_dtype="E")
        self.dec = set_column_properties(
            "SHE_BFD_TRAINING_UPDATED_DEC", comment="deg", dtype=">f8", fits_dtype="D")
        self.dec_err = set_column_properties(
            "SHE_BFD_TRAINING_UPDATED_DEC_ERR", comment="deg" , dtype=">f8", fits_dtype="E")
        self.moments = set_column_properties(
            "SHE_BFD_TRAINING_MOMENTS" , dtype=">f4", fits_dtype="E", length=7)
        self.dm_dg1 = set_column_properties(
            "SHE_BFD_TRAINING_DM_DG1" , dtype=">f4", fits_dtype="E", length=7)
        self.dm_dg2 = set_column_properties(
            "SHE_BFD_TRAINING_DM_DG2" , dtype=">f4", fits_dtype="E", length=7)
        self.dm_dmu = set_column_properties(
            "SHE_BFD_TRAINING_DM_DMU" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dg1dg1 = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DG1DG1" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dg1dg2 = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DG1DG2" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dg2dg2 = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DG2DG2" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dg1dmu = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DG1DMU" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dg2dmu = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DG2DMU" , dtype=">f4", fits_dtype="E", length=7)
        self.d2m_dmudmu = set_column_properties(
            "SHE_BFD_TRAINING_D2M_DMUDMU" , dtype=">f4", fits_dtype="E", length=7)
        self.tmp_wgt = set_column_properties(
            "SHE_BFD_TRAINING_TMPL_WEIGHT" , dtype=">f4", fits_dtype="E")
        self.jsupp = set_column_properties(
            "SHE_BFD_TRAINING_JSUPPRESS" , dtype=">f4", fits_dtype="E") 

        
        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
bfd_training_table_format = KsbTrainingTableFormat()

# And a convient alias for it
tf = bfd_training_table_format


def make_bfd_training_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.version] = tf.__version__
    header[tf.m.format] = tf.m.table_format

    return header


def initialise_bfd_training_table(optional_columns=None):
    """
        @brief Initialise a galaxy population table.

        @return bfd_training_table <astropy.Table>
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
            init_cols.append([])
            dtypes.append((tf.dtypes[colname], tf.lengths[colname]))

    bfd_training_table = Table(init_cols, names=names, dtype=dtypes)

    bfd_training_table.meta = make_bfd_training_table_header()

    assert(is_in_format(bfd_training_table, tf))

    return bfd_training_table
