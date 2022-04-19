""" @file she_lensmc_measurements.py

    Created 6 Dec 2017

    Format definition for lensmc measurements tables.
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

__updated__ = "2021-08-12"

from collections import OrderedDict

from ..flags import she_flag_version
from ..logging import getLogger
from ..table_formats.mer_final_catalog import tf as mfc_tf
from ..table_formats.she_measurements import SheMeasurementsFormat, SheMeasurementsMeta
from ..table_utility import init_table, is_in_format

fits_version = "8.0"
fits_def = "she.lensmcMeasurements"

child_label = "SHE_LENSMC_"

logger = getLogger(__name__)


class SheLensMcMeasurementsMeta(SheMeasurementsMeta):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def


def set_lensmc_column_properties(tf):
    """ Common function for setting column properties for columns unique to LensMC, to allow
        reuse with the she_lensmc_tu_matched table.
    """
    tf.snr_err = tf.set_column_properties(
        "SHE_LENSMC_SNR_ERR", dtype = ">f4", fits_dtype = "E")
    tf.bulge_frac = tf.set_column_properties(
        "SHE_LENSMC_BULGE_FRAC", dtype = ">f4", fits_dtype = "E")
    tf.bulge_frac_err = tf.set_column_properties(
        "SHE_LENSMC_BULGE_FRAC_ERR", dtype = ">f4", fits_dtype = "E")
    tf.gal_pvalue = tf.set_column_properties(
        "SHE_LENSMC_GAL_PVALUE", dtype = ">f4", fits_dtype = "E")
    tf.chi2 = tf.set_column_properties(
        "SHE_LENSMC_CHI2", dtype = ">f4", fits_dtype = "E")
    tf.dof = tf.set_column_properties(
        "SHE_LENSMC_DOF", dtype = ">i4", fits_dtype = "K")
    tf.acc = tf.set_column_properties(
        "SHE_LENSMC_ACCEPTANCE", dtype = ">f4", fits_dtype = "E")
    tf.m1_ical = tf.set_column_properties(
        "SHE_LENSMC_M1_ICAL", dtype = ">f4", fits_dtype = "E")
    tf.m2_ical = tf.set_column_properties(
        "SHE_LENSMC_M2_ICAL", dtype = ">f4", fits_dtype = "E")


class SheLensMcMeasurementsFormat(SheMeasurementsFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the lensmc_measurements_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = SheLensMcMeasurementsMeta

    def __init__(self):
        super().__init__(finalize = False)

        self.setup_child_table_format(child_label)

        # LensMC specific columns
        set_lensmc_column_properties(self)

        self._finalize_init()

    @staticmethod
    def init_table(*args, **kwargs):
        """ Bound alias to the free table initialisation function, using this table format.
        """

        return initialise_lensmc_measurements_table(*args, **kwargs)


# Define an instance of this object that can be imported
lensmc_measurements_table_format = SheLensMcMeasurementsFormat()

# And a convenient alias for it
tf = lensmc_measurements_table_format


def make_lensmc_measurements_table_header(
        model_hash = None,
        model_seed = None,
        noise_seed = None,
        observation_id = None,
        pointing_id = None,
        observation_time = None,
        tile_id = None, ):
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


def initialise_lensmc_measurements_table(mer_final_catalog = None,
                                         size = None,
                                         optional_columns = None,
                                         init_cols = None,
                                         model_hash = None,
                                         model_seed = None,
                                         noise_seed = None,
                                         observation_id = None,
                                         pointing_id = None,
                                         observation_time = None,
                                         tile_id = None,
                                         ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param mer_final_catalog <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @param detector <int?> Detector this table corresponds to

        @return lensmc_measurements_table <astropy.table.Table>
    """

    assert (mer_final_catalog is None) or (
        is_in_format(mer_final_catalog, mfc_tf, strict = False))

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    lensmc_measurements_table = init_table(tf, optional_columns = optional_columns, init_cols = init_cols, size = size)

    lensmc_measurements_table.meta = make_lensmc_measurements_table_header(
        model_hash = model_hash,
        model_seed = model_seed,
        noise_seed = noise_seed,
        observation_id = observation_id,
        pointing_id = pointing_id,
        observation_time = observation_time,
        tile_id = tile_id)

    assert is_in_format(lensmc_measurements_table, tf)

    return lensmc_measurements_table
