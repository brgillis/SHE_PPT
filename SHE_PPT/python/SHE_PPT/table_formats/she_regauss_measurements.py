""" @file regauss_measurements.py

    Created 6 Dec 2017

    Format definition for regauss measurements tables.
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

from astropy.table import Table

from SHE_PPT import detector as dtc
from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.logging import getLogger
from SHE_PPT.table_formats.mer_final_catalog import tf as mfc_tf
from SHE_PPT.table_formats.she_measurements import SheMeasurementsMeta, SheMeasurementsFormat
from SHE_PPT.table_utility import is_in_format, setup_table_format, set_column_properties, init_table, setup_child_table_format, set_column_properties, init_table

fits_version = "8.0"
fits_def = "she.regaussMeasurements"

child_label = "SHE_REGAUSS_"

logger = getLogger(mv.logger_name)


class SheRegaussMeasurementsMeta(SheMeasurementsMeta):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        # Inherit meta format from parent class
        super().__init__()

        self.__version__ = fits_version
        self.table_format = fits_def

        return


class SheRegaussMeasurementsFormat(SheMeasurementsFormat):
    """
        @brief A class defining the format for shear estimates tables. Only the regauss_measurements_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Inherit format from parent class, and save it in separate dicts so we can properly adjust column names
        super().__init__()

        # Get the metadata (contained within its own class)
        self.meta = SheRegaussMeasurementsMeta()

        setup_child_table_format(self, child_label, unlabelled_columns=["OBJECT_ID"])

        # regauss specific columns
        self.re = set_column_properties(self,
            "SHE_REGAUSS_RE", is_optional=False, dtype=">f4", fits_dtype="E")
        self.re_err = set_column_properties(self,
            "SHE_REGAUSS_RE_ERR", is_optional=False, dtype=">f4", fits_dtype="E")
        self.flux = set_column_properties(self,
            "SHE_REGAUSS_FLUX", is_optional=False, dtype=">f4", fits_dtype="E")
        self.flux_err = set_column_properties(self,
            "SHE_REGAUSS_FLUX_ERR", is_optional=False, dtype=">f4", fits_dtype="E")
        self.snr = set_column_properties(self,
            "SHE_REGAUSS_SNR", is_optional=False, dtype=">f4", fits_dtype="E")
        self.snr_err = set_column_properties(self,
            "SHE_REGAUSS_SNR_ERR", is_optional=False, dtype=">f4", fits_dtype="E")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
regauss_measurements_table_format = SheRegaussMeasurementsFormat()

# And a convient alias for it
tf = regauss_measurements_table_format


def make_regauss_measurements_table_header(
                                  model_hash=None,
                                  model_seed=None,
                                  noise_seed=None,
                                  observation_id=None,
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
    header[tf.m.observation_time] = observation_time
    header[tf.m.tile_id] = tile_id

    header[tf.m.valid] = "UNKNOWN"

    return header


def initialise_regauss_measurements_table(mer_final_catalog=None,
                                 size=None,
                                 optional_columns=None,
                                 init_cols=None,
                                 model_hash=None,
                                 model_seed=None,
                                 noise_seed=None,
                                 observation_id=None,
                                 observation_time=None,
                                 tile_id=None,
                                 ):
    """
        @brief Initialise a shear estimates table based on a detections table, with the
               desired set of optional columns

        @param mer_final_catalog <astropy.table.Table>

        @param optional_columns <list<str>> List of names for optional columns to include.
               Default is gal_e1_err and gal_e2_err

        @return regauss_measurements_table <astropy.table.Table>
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

    regauss_measurements_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    if mer_final_catalog is not None:
        if model_hash is None:
            model_hash = mer_final_catalog.meta[mfc_tf.m.model_hash]
        if model_seed is None:
            model_seed = mer_final_catalog.meta[mfc_tf.m.model_seed]
        if noise_seed is None:
            noise_seed = mer_final_catalog.meta[mfc_tf.m.noise_seed]

    regauss_measurements_table.meta = make_regauss_measurements_table_header(
                                                           model_hash=model_hash,
                                                           model_seed=model_seed,
                                                           noise_seed=noise_seed,
                                                           observation_id=observation_id,
                                                           observation_time=observation_time,
                                                           tile_id=tile_id)

    assert(is_in_format(regauss_measurements_table, tf))

    return regauss_measurements_table
