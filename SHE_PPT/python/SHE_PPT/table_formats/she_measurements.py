""" @file she_measurements.py

    Created 2020-07-03

    Base format definition for common properties of all shear measurements tables.
"""

__updated__ = "2021-08-12"

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
from typing import List

from SHE_PPT.constants.fits import (she_flag_version_label, model_hash_label,
                                    model_seed_label, noise_seed_label, obs_id_label, pnt_id_label,
                                    obs_time_label, tile_id_label, valid_label)
from ..constants.fits import fits_version_label, fits_def_label
from ..table_utility import SheTableFormat


fits_version = "8.0"
fits_def = "she.measurements"


class SheMeasurementsMeta():
    """ A class defining the metadata common to shear measurements tables.
    """

    def __init__(self):

        self.table_format = fits_def
        self.__version__ = fits_version

        # Table metadata labels
        self.fits_version = fits_version_label
        self.fits_def = fits_def_label
        self.she_flag_version = she_flag_version_label
        self.model_hash = model_hash_label
        self.model_seed = model_seed_label
        self.noise_seed = noise_seed_label
        self.observation_id = obs_id_label
        self.pointing_id = pnt_id_label
        self.observation_time = obs_time_label
        self.tile_id = tile_id_label

        self.valid = valid_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.she_flag_version, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.observation_id, "Individual ID or list of IDs"),
                                     (self.pointing_id, "List of pointing IDs"),
                                     (self.observation_time, "Individual time or list of times"),
                                     (self.tile_id, "Individual ID or list of IDs"),
                                     (self.valid,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheMeasurementsFormat(SheTableFormat):
    """  A class defining the columns common to shear estimates tables. Only the measurements_table_format
         instance of this should generally be accessed, and it should not be changed.
    """

    is_base = True
    unlabelled_columns: List[str]

    def __init__(self,
                 meta=None,
                 finalize=True):
        if meta is None:
            meta = SheMeasurementsMeta()
        super().__init__(meta)

        # Table column labels and properties

        self.ID = self.set_column_properties("OBJECT_ID", dtype=">i8", fits_dtype="K", unlabelled=True)

        # Fit information

        self.fit_flags = self.set_column_properties(
            "FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = self.set_column_properties(
            "VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = self.set_column_properties(
            "FIT_CLASS", dtype=">i2", fits_dtype="I")
        self.nexp = self.set_column_properties(
            "NEXP", dtype=">i2", fits_dtype="I")
        self.unmasked_fraction = self.set_column_properties(
            "UNMASKED_FRACTION", dtype=">f4", fits_dtype="E")
        self.rec_flags = self.set_column_properties(
            "REC_FLAGS", dtype=">i8", fits_dtype="K")

        # Shear/shape information

        self.g1 = self.set_column_properties(
            "G1", dtype=">f4", fits_dtype="E")
        self.g1_err = self.set_column_properties(
            "G1_ERR", dtype=">f4", fits_dtype="E")
        self.e1_err = self.set_column_properties(
            "E1_ERR", dtype=">f4", fits_dtype="E")
        self.g2 = self.set_column_properties(
            "G2", dtype=">f4", fits_dtype="E")
        self.g2_err = self.set_column_properties(
            "G2_ERR", dtype=">f4", fits_dtype="E")
        self.e2_err = self.set_column_properties(
            "E2_ERR", dtype=">f4", fits_dtype="E")
        self.e_var = self.set_column_properties(
            "E_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1g2_covar = self.set_column_properties(
            "G1G2_COVAR", dtype=">f4", fits_dtype="E")
        self.e1e2_covar = self.set_column_properties(
            "E1E2_COVAR", dtype=">f4", fits_dtype="E")
        self.weight = self.set_column_properties(
            "SHEAR_WEIGHT", dtype=">f4", fits_dtype="E")
        self.shape_weight = self.set_column_properties(
            "SHAPE_WEIGHT", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1_uncal = self.set_column_properties(
            "G1_UNCAL", dtype=">f4", fits_dtype="E")
        self.g1_uncal_err = self.set_column_properties(
            "G1_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.e1_uncal_err = self.set_column_properties(
            "E1_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.g2_uncal = self.set_column_properties(
            "G2_UNCAL", dtype=">f4", fits_dtype="E")
        self.g2_uncal_err = self.set_column_properties(
            "G2_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.e2_uncal_err = self.set_column_properties(
            "E2_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.e_uncal_var = self.set_column_properties(
            "E_UNCAL_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1g2_uncal_covar = self.set_column_properties(
            "G1G2_UNCAL_COVAR", dtype=">f4", fits_dtype="E")
        self.e1e2_uncal_covar = self.set_column_properties(
            "E1E2_UNCAL_COVAR", dtype=">f4", fits_dtype="E")
        self.weight_uncal = self.set_column_properties(
            "SHEAR_WEIGHT_UNCAL", dtype=">f4", fits_dtype="E")
        self.shape_weight_uncal = self.set_column_properties(
            "SHAPE_WEIGHT_UNCAL", dtype=">f4", fits_dtype="E")
        self.shape_noise = self.set_column_properties(
            "ASSUMED_SHAPE_NOISE", dtype=">f4", fits_dtype="E", is_optional=True)

        self.ra = self.set_column_properties(
            "UPDATED_RA", dtype=">f8", fits_dtype="D", comment="deg")
        self.ra_err = self.set_column_properties(
            "UPDATED_RA_ERR", dtype=">f4", fits_dtype="E", comment="deg")
        self.dec = self.set_column_properties(
            "UPDATED_DEC", dtype=">f8", fits_dtype="D", comment="deg")
        self.dec_err = self.set_column_properties(
            "UPDATED_DEC_ERR", dtype=">f4", fits_dtype="E", comment="deg")

        # Information on other galaxy properties

        self.re = self.set_column_properties(
            "RE", dtype=">f4", fits_dtype="E")
        self.re_err = self.set_column_properties(
            "RE_ERR", dtype=">f4", fits_dtype="E")
        self.flux = self.set_column_properties(
            "FLUX", dtype=">f4", fits_dtype="E")
        self.flux_err = self.set_column_properties(
            "FLUX_ERR", dtype=">f4", fits_dtype="E")
        self.snr = self.set_column_properties(
            "SNR", dtype=">f4", fits_dtype="E")

        if finalize:
            self._finalize_init()


# Define an instance of this object that can be imported
she_measurements_table_format = SheMeasurementsFormat()

# And a convenient alias for it
tf = she_measurements_table_format
