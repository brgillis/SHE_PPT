""" @file bfd_moments.py

    Created 6 Dec 2017

    Format definition for BFD moments tables.
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

__updated__ = "2021-02-16"

from collections import OrderedDict

from .. import magic_values as mv
from ..flags import she_flag_version
from ..logging import getLogger
from ..table_formats.mer_final_catalog import tf as mfc_tf
from ..table_utility import is_in_format, init_table, SheTableFormat


fits_version = "8.0"
fits_def = "she.bfdMoments"

logger = getLogger(mv.logger_name)


class BfdMomentsMeta():
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label
        self.she_flag_version = mv.she_flag_version_label
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        self.observation_id = mv.obs_id_label
        self.observation_time = mv.obs_time_label
        self.tile_id = mv.tile_id_label
        self.nlost = "NLOST"
        self.wt_n = "WT_N"
        self.wt_sigma = "WT_SIGMA"

        self.valid = mv.valid_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.fits_def, None),
                                     (self.she_flag_version, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.observation_id, None),
                                     (self.observation_time, None),
                                     (self.tile_id, None),
                                     (self.nlost, None),
                                     (self.wt_n, None),
                                     (self.wt_sigma, None),
                                     (self.valid,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class BfdMomentsFormat(SheTableFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the bfd_moments_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(BfdMomentsMeta())

        # Table column labels and properties

        self.ID = self.set_column_properties(
                                        "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.fit_flags = self.set_column_properties(
                                               "SHE_BFD_FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = self.set_column_properties(
                                               "SHE_BFD_VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = self.set_column_properties(
                                               "SHE_BFD_FIT_CLASS", dtype=">i2", fits_dtype="I")
        self.updated_ra = self.set_column_properties(
                                                "SHE_BFD_UPDATED_RA", is_optional=False, comment="deg")
        self.updated_ra_err = self.set_column_properties(
                                                "SHE_BFD_UPDATED_RA_ERR", is_optional=False, comment="deg")
        self.updated_dec = self.set_column_properties(
                                                 "SHE_BFD_UPDATED_DEC", is_optional=True, comment="deg")
        self.updated_dec_err = self.set_column_properties(
                                                "SHE_BFD_UPDATED_DEC_ERR", is_optional=True, comment="deg")

        # BFD specific columns
        self.bfd_moments = self.set_column_properties(
                                        "SHE_BFD_MOMENTS", is_optional=True, dtype=">f4", fits_dtype="E", length=7)
        self.bfd_pqr = self.set_column_properties(
                                        "SHE_BFD_PQR", is_optional=True, dtype=">f4", fits_dtype="E", length=6)
        self.bfd_cov_even = self.set_column_properties(
                                        "SHE_BFD_COV_EVEN", is_optional=True, dtype=">f4", fits_dtype="E", length=15)
        self.bfd_cov_odd = self.set_column_properties(
                                        "SHE_BFD_COV_ODD", is_optional=True, dtype=">f4", fits_dtype="E", length=3)

        self._finalize_init()


# Define an instance of this object that can be imported
bfd_moments_table_format = BfdMomentsFormat()

# And a convient alias for it
tf = bfd_moments_table_format


def make_bfd_moments_table_header(model_hash=None,
                                  model_seed=None,
                                  noise_seed=None,
                                  observation_id=None,
                                  observation_time=None,
                                  tile_id=None,
                                  nlost=None,
                                  wt_n=None,
                                  wt_sigma=None):
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
    header[tf.m.she_flag_version] = she_flag_version

    header[tf.m.model_hash] = model_hash
    header[tf.m.model_seed] = model_seed
    header[tf.m.noise_seed] = noise_seed

    header[tf.m.observation_id] = observation_id
    header[tf.m.observation_time] = observation_time
    header[tf.m.tile_id] = tile_id

    header[tf.m.nlost] = nlost
    header[tf.m.wt_n] = wt_n
    header[tf.m.wt_sigma] = wt_sigma

    header[tf.m.valid] = "UNKNOWN"

    return header


def initialise_bfd_moments_table(mer_final_catalog=None,
                                 size=None,
                                 optional_columns=None,
                                 init_cols=None,
                                 model_hash=None,
                                 model_seed=None,
                                 noise_seed=None,
                                 observation_id=None,
                                 observation_time=None,
                                 tile_id=None,
                                 nlost=None,
                                 wt_n=None,
                                 wt_sigma=None,
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

        @return bfd_moments_table <astropy.table.Table>
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

    bfd_moments_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    bfd_moments_table.meta = make_bfd_moments_table_header(model_hash=model_hash,
                                                           model_seed=model_seed,
                                                           noise_seed=noise_seed,
                                                           observation_id=observation_id,
                                                           observation_time=observation_time,
                                                           tile_id=tile_id,
                                                           nlost=nlost,
                                                           wt_n=wt_n,
                                                           wt_sigma=wt_sigma)

    assert is_in_format(bfd_moments_table, tf)

    return bfd_moments_table
