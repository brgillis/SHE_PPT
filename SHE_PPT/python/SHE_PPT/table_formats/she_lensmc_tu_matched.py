""" @file she_lensmc_tu_matched.py

    Created 2021/08/10

    Format definition for lensmc tu_matched tables.
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

__updated__ = "2021-08-10"

from collections import OrderedDict

from .. import magic_values as mv
from ..flags import she_flag_version
from ..logging import getLogger
from ..table_formats.mer_final_catalog import tf as mfc_tf
from ..table_formats.she_tu_matched import SheTUMatchedMeta, SheTUMatchedFormat
from ..table_utility import is_in_format, init_table


fits_version = "8.0"
fits_def = "she.lensmc_tu_matched"

child_label = "SHE_LENSMC_"

logger = getLogger(mv.logger_name)


class SheLensMcTUMatchedMeta(SheTUMatchedMeta):
    """ A class defining the metadata for LensMC TU Matched tables.
    """

    def __init__(self):

        # Inherit meta format from parent class
        super().__init__(table_format=fits_def,
                         version=fits_version,)


class SheLensMcTUMatchedFormat(SheTUMatchedFormat):
    """ A class defining the format for LensMC TU Matched tables. Only the lensmc_tu_matched_table_format
        instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__(SheLensMcTUMatchedMeta(), finalize=False)

        self.setup_child_table_format(child_label)

        # lensmc specific columns
        # TODO: Make this common code with she_lensmc_measurements
        self.snr_err = self.set_column_properties(
            "SHE_LENSMC_SNR_ERR", dtype=">f4", fits_dtype="E")
        self.bulge_frac = self.set_column_properties(
            "SHE_LENSMC_BULGE_FRAC", dtype=">f4", fits_dtype="E")
        self.bulge_frac_err = self.set_column_properties(
            "SHE_LENSMC_BULGE_FRAC_ERR", dtype=">f4", fits_dtype="E")
        self.gal_pvalue = self.set_column_properties(
            "SHE_LENSMC_GAL_PVALUE", dtype=">f4", fits_dtype="E")
        self.chi2 = self.set_column_properties(
            "SHE_LENSMC_CHI2", dtype=">f4", fits_dtype="E")
        self.dof = self.set_column_properties(
            "SHE_LENSMC_DOF", dtype=">i4", fits_dtype="K")
        self.acc = self.set_column_properties(
            "SHE_LENSMC_ACCEPTANCE", dtype=">f4", fits_dtype="E")
        self.m1_ical = self.set_column_properties(
            "SHE_LENSMC_M1_ICAL", dtype=">f4", fits_dtype="E")
        self.m2_ical = self.set_column_properties(
            "SHE_LENSMC_M2_ICAL", dtype=">f4", fits_dtype="E")

        self._finalize_init()


# Define an instance of this object that can be imported
lensmc_tu_matched_table_format = SheLensMcTUMatchedFormat()

# And a convient alias for it
tf = lensmc_tu_matched_table_format


def make_lensmc_tu_matched_table_header(
        model_hash=None,
        model_seed=None,
        noise_seed=None,
        observation_id=None,
        pointing_id=None,
        observation_time=None,
        tile_id=None,):
    """
        @brief Generate a header for a shear estimates table.

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
    header[tf.m.pointing_id] = pointing_id
    header[tf.m.observation_time] = observation_time
    header[tf.m.tile_id] = tile_id

    header[tf.m.valid] = "UNKNOWN"

    return header


def initialise_lensmc_tu_matched_table(mer_final_catalog=None,
                                       size=None,
                                       optional_columns=None,
                                       init_cols=None,
                                       model_hash=None,
                                       model_seed=None,
                                       noise_seed=None,
                                       observation_id=None,
                                       pointing_id=None,
                                       observation_time=None,
                                       tile_id=None,
                                       ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param mer_final_catalog <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector <int?> Detector this table corresponds to

        @return lensmc_tu_matched_table <astropy.table.Table>
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

    lensmc_tu_matched_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    lensmc_tu_matched_table.meta = make_lensmc_tu_matched_table_header(
        model_hash=model_hash,
        model_seed=model_seed,
        noise_seed=noise_seed,
        observation_id=observation_id,
        pointing_id=pointing_id,
        observation_time=observation_time,
        tile_id=tile_id)

    assert is_in_format(lensmc_tu_matched_table, tf)

    return lensmc_tu_matched_table
