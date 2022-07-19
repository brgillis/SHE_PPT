""" @file she_lensmc_chains.py

    Created 6 Dec 2017

    Format definition for lensmc chains tables.
"""

__updated__ = "2022-01-18"

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

from ..constants.fits import (EXTNAME_LABEL, FITS_DEF_LABEL, FITS_VERSION_LABEL, MODEL_HASH_LABEL, MODEL_SEED_LABEL,
                              NOISE_SEED_LABEL, OBS_ID_LABEL, OBS_TIME_LABEL, PNT_ID_LABEL, SHE_FLAG_VERSION_LABEL,
                              TILE_ID_LABEL, VALID_LABEL, )
from ..constants.shear_estimation_methods import ShearEstimationMethods
from ..flags import she_flag_version
from ..logging import getLogger
from ..table_formats.mer_final_catalog import tf as mfc_tf
from ..table_utility import SheTableFormat, SheTableMeta, init_table, is_in_format

fits_version = "8.0"
fits_def = "she.lensmcChains"

num_chains = 1
len_chain = 200
total_chain_length = num_chains * len_chain

logger = getLogger(__name__)


class SheLensMcChainsMeta(SheTableMeta):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL
    extname: str = EXTNAME_LABEL
    she_flag_version: str = SHE_FLAG_VERSION_LABEL
    model_hash: str = MODEL_HASH_LABEL
    model_seed: str = MODEL_SEED_LABEL
    noise_seed: str = NOISE_SEED_LABEL
    observation_id: str = OBS_ID_LABEL
    pointing_id: str = PNT_ID_LABEL
    observation_time: str = OBS_TIME_LABEL
    tile_id: str = TILE_ID_LABEL
    method: str = "SEMETHOD"
    len_chain: str = "LCHAIN"

    valid = VALID_LABEL

    def __init__(self):
        # Store the less-used comments in a dict
        super().__init__(comments=OrderedDict(((self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.she_flag_version, None),
                                               (self.model_hash, None),
                                               (self.model_seed, None),
                                               (self.noise_seed, None),
                                               (self.observation_id, None),
                                               (self.pointing_id, "List of pointing IDs"),
                                               (self.observation_time, None),
                                               (self.tile_id, None),
                                               (self.method, "Shear estimation method used to generate these chains"),
                                               (self.len_chain, None),
                                               (self.valid, "0: Not tested; 1: Pass; -1: Fail")
                                               )))


class SheLensMcChainsFormat(SheTableFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the lensmc_chains_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = SheLensMcChainsMeta

    def __init__(self):
        super().__init__()

        # Table column labels and properties

        self.ID = self.set_column_properties(
            "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.fit_flags = self.set_column_properties(
            "SHE_LENSMC_FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = self.set_column_properties(
            "SHE_LENSMC_VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = self.set_column_properties(
            "SHE_LENSMC_FIT_CLASS", dtype=">i2", fits_dtype="I")
        self.weight = self.set_column_properties(
            "SHE_LENSMC_CHAINS_SHEAR_WEIGHT", dtype=">f4", fits_dtype="E")
        self.shape_weight = self.set_column_properties(
            "SHE_LENSMC_CHAINS_SHAPE_WEIGHT", dtype=">f4",
            fits_dtype="E", is_optional=True)
        self.e_var = self.set_column_properties(
            "SHE_LENSMC_E_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.shape_noise = self.set_column_properties(
            "SHE_LENSMC_ASSUMED_SHAPE_NOISE", dtype=">f4",
            fits_dtype="E", is_optional=True)

        self.g1 = self.set_column_properties(
            "SHE_LENSMC_G1_CHAIN", dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.g2 = self.set_column_properties(
            "SHE_LENSMC_G2_CHAIN", dtype=">f4", fits_dtype="E",
            length=total_chain_length)

        self.ra = self.set_column_properties(
            "SHE_LENSMC_UPDATED_RA_CHAIN", is_optional=True, comment="deg",
            fits_dtype="D", length=total_chain_length)
        self.dec = self.set_column_properties(
            "SHE_LENSMC_UPDATED_DEC_CHAIN", is_optional=True, comment="deg",
            fits_dtype="D", length=total_chain_length)

        # lensmc specific columns
        self.re = self.set_column_properties(
            "SHE_LENSMC_RE_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.flux = self.set_column_properties(
            "SHE_LENSMC_FLUX_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.magnitude = self.set_column_properties(
            "SHE_LENSMC_MAGNITUDE_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.bulge_frac = self.set_column_properties(
            "SHE_LENSMC_BULGE_FRAC_CHAIN", is_optional=True, dtype=">f4",
            fits_dtype="E", length=total_chain_length)
        self.snr = self.set_column_properties(
            "SHE_LENSMC_SNR_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.lr = self.set_column_properties(
            "SHE_LENSMC_LR_CHAIN", is_optional=True, dtype=">f4", fits_dtype="E",
            length=total_chain_length)
        self.chi2 = self.set_column_properties(
            "SHE_LENSMC_CHI2", is_optional=True, dtype=">f4", fits_dtype="E")
        self.dof = self.set_column_properties(
            "SHE_LENSMC_DOF", is_optional=True, dtype=">f4", fits_dtype="E")
        self.acc = self.set_column_properties(
            "SHE_LENSMC_ACCEPTANCE", is_optional=True, dtype=">f4", fits_dtype="E")
        self.nexp = self.set_column_properties(
            "SHE_LENSMC_NEXP", is_optional=True, dtype=">f4", fits_dtype="E")

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_lensmc_chains_table(*args, **kwargs)


# Define an instance of this object that can be imported
lensmc_chains_table_format = SheLensMcChainsFormat()

# And a convenient alias for it
tf = lensmc_chains_table_format


def make_lensmc_chains_table_header(model_hash=None,
                                    model_seed=None,
                                    noise_seed=None,
                                    observation_id=None,
                                    pointing_id=None,
                                    observation_time=None,
                                    method=ShearEstimationMethods.LENSMC.value,
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
                                   method=ShearEstimationMethods.LENSMC.value,
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

    lensmc_chains_table.meta = make_lensmc_chains_table_header(model_hash=model_hash,
                                                               model_seed=model_seed,
                                                               noise_seed=noise_seed,
                                                               observation_id=observation_id,
                                                               pointing_id=pointing_id,
                                                               observation_time=observation_time,
                                                               method=method,
                                                               tile_id=tile_id, )

    assert is_in_format(lensmc_chains_table, tf)

    return lensmc_chains_table
