""" @file she_lensmc_chains.py

    Created 6 Dec 2017

    Format definition for lensmc chains tables.
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

<<<<<<< HEAD
__updated__ = "2020-09-23"
=======
__updated__ = "2020-09-23"
>>>>>>> refs/remotes/origin/brg--dm_updates2

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_utility import is_in_format, setup_table_format, set_column_properties, init_table

fits_version = "8.0"
fits_def = "she.lensmcChains"

num_chains = 1
len_chain = 200
total_chain_length = num_chains * len_chain

logger = getLogger(mv.logger_name)


class SheLensMcChainsMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label
        self.extname = mv.extname_label
        self.she_flag_version = mv.she_flag_version_label
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        self.observation_id = mv.obs_id_label
        self.pointing_id = mv.pnt_id_label
        self.observation_time = mv.obs_time_label
        self.tile_id = mv.tile_id_label
        self.method = "SEMETHOD"
        self.len_chain = "LCHAIN"

        self.valid = mv.valid_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.she_flag_version, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
<<<<<<< HEAD
                                     (self.observation_id, "Individual ID or list of IDs"),
                                     (self.pointing_id, "List of pointing IDs"),
                                     (self.observation_time, "Individual time or list of times"),
                                     (self.tile_id, "Individual ID or list of IDs"),
=======
                                     (self.observation_id, None),
                                     (self.observation_time, None),
                                     (self.tile_id, None),
                                     (self.method, "Shear estimation method used to generate these chains"),
>>>>>>> refs/remotes/origin/brg--dm_updates2
                                     (self.len_chain, None),
                                     (self.valid,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheLensMcChainsFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the lensmc_chains_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = SheLensMcChainsMeta()

        setup_table_format(self)

        # Table column labels and properties

        self.ID = set_column_properties(self,
                                        "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.fit_flags = set_column_properties(self,
                                               "SHE_LENSMC_FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = set_column_properties(self,
                                               "SHE_LENSMC_VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties(self,
                                               "SHE_LENSMC_FIT_CLASS", dtype=">i2", fits_dtype="I")
        self.weight = set_column_properties(self,
                                            "SHE_LENSMC_CHAINS_SHEAR_WEIGHT", dtype=">f4", fits_dtype="E")
        self.shape_weight = set_column_properties(self,
                                                  "SHE_LENSMC_CHAINS_SHAPE_WEIGHT", dtype=">f4", fits_dtype="E", is_optional=True)
        self.e_var = set_column_properties(self,
                                           "SHE_LENSMC_E_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.shape_noise = set_column_properties(self,
                                                 "SHE_LENSMC_ASSUMED_SHAPE_NOISE", dtype=">f4", fits_dtype="E", is_optional=True)

        self.g1 = set_column_properties(self,
                                        "SHE_LENSMC_G1_CHAIN", dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.g2 = set_column_properties(self,
                                        "SHE_LENSMC_G2_CHAIN", dtype=">f4", fits_dtype="E", length=total_chain_length)

        self.ra = set_column_properties(self,
                                        "SHE_LENSMC_UPDATED_RA_CHAIN", is_optional=True, comment="deg", fits_dtype="D", length=total_chain_length)
        self.dec = set_column_properties(self,
                                         "SHE_LENSMC_UPDATED_DEC_CHAIN", is_optional=True, comment="deg", fits_dtype="D", length=total_chain_length)

        # lensmc specific columns
        self.re = set_column_properties(self,
                                        "SHE_LENSMC_RE_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.flux = set_column_properties(self,
                                          "SHE_LENSMC_FLUX_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.bulge_frac = set_column_properties(self,
                                                "SHE_LENSMC_BULGE_FRAC_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.snr = set_column_properties(self,
                                         "SHE_LENSMC_SNR_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.lr = set_column_properties(self,
                                        "SHE_LENSMC_LR_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E", length=total_chain_length)
        self.chi2 = set_column_properties(self,
                                          "SHE_LENSMC_CHI2", is_optional=True, dtype=">f4", fits_dtype="E")
        self.dof = set_column_properties(self,
                                         "SHE_LENSMC_DOF", is_optional=True, dtype=">f4", fits_dtype="E")
        self.acc = set_column_properties(self,
                                         "SHE_LENSMC_ACCEPTANCE", is_optional=True, dtype=">f4", fits_dtype="E")
        self.nexp = set_column_properties(self,
                                          "SHE_LENSMC_NEXP", is_optional=True, dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
lensmc_chains_table_format = SheLensMcChainsFormat()

# And a convient alias for it
tf = lensmc_chains_table_format



def make_lensmc_chains_table_header(model_hash=None,
                                    model_seed=None,
                                    noise_seed=None,
                                    observation_id=None,
                                    pointing_id=None,
                                    observation_time=None,
                                    method="LensMC",
                                    tile_id=None):
    """
        @brief Generate a header for a shear estimates table.

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param model_hash <int> Hash of the physical model options dictionary

        @param model_seed <int> Full seed used for the physical model for this image

        @param noise_seed <int> Seed used for generating noise for this image

        @return header <dict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def
    header[tf.m.she_flag_version] = she_flag_version

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    header[tf.m.observation_id] = observation_id
    header[tf.m.pointing_id] = pointing_id
    header[tf.m.observation_time] = observation_time
    header[tf.m.tile_id] = tile_id

    header[tf.m.method] = method
    header[tf.m.len_chain] = len_chain

    header[tf.m.fits_def] = fits_def

    header[tf.m.valid] = "UNKNOWN"

    return header


def initialise_lensmc_chains_table(mer_final_catalog=None,
                                   size=None,
                                   optional_columns=None,
                                   init_cols=None,
                                   model_hash=None,
                                   model_seed=None,
                                   noise_seed=None,
                                   observation_id=None,
                                   pointing_id=None,
                                   observation_time=None,
                                   method="LensMC",
                                   tile_id=None,
                                   ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param mer_final_catalog <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector_x <int> x-index (1-6) for detector this image was taken with

        @param detector_y <int> y-index (1-6) for detector this image was taken with

        @param detector <int?> Detector this table corresponds to

        @return lensmc_chains_table <astropy.table.Table>
    """

    assert (mer_final_catalog is None) or (
        is_in_format(mer_final_catalog, mfc_tf, strict=False))

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    lensmc_chains_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    if mer_final_catalog is not None:
        if model_hash is None:
            model_hash = mer_final_catalog.meta[mfc_tf.m.model_hash]
        if model_seed is None:
            model_seed = mer_final_catalog.meta[mfc_tf.m.model_seed]
        if noise_seed is None:
            noise_seed = mer_final_catalog.meta[mfc_tf.m.noise_seed]

    lensmc_chains_table.meta = make_lensmc_chains_table_header(model_hash=model_hash,
                                                               model_seed=model_seed,
                                                               noise_seed=noise_seed,
                                                               observation_id=observation_id,
                                                               pointing_id=pointing_id,
                                                               observation_time=observation_time,
                                                               method=method,
                                                               tile_id=tile_id,)

    assert(is_in_format(lensmc_chains_table, tf))

    return lensmc_chains_table
