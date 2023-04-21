""" @file she_measurements.py

    Created 2020-07-03

    Base format definition for common properties of all shear measurements tables.
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

from typing import List

from ..constants.fits import (FITS_DEF_LABEL, FITS_VERSION_LABEL, MODEL_HASH_LABEL, MODEL_SEED_LABEL, NOISE_SEED_LABEL,
                              OBS_ID_LABEL, OBS_TIME_LABEL, PNT_ID_LABEL, SHE_FLAG_VERSION_LABEL, TILE_ID_LABEL,
                              VALID_LABEL, )
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.measurements"


class SheMeasurementsMeta(SheTableMeta):
    """ A class defining the metadata common to shear measurements tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL
    she_flag_version: str = SHE_FLAG_VERSION_LABEL
    model_hash: str = MODEL_HASH_LABEL
    model_seed: str = MODEL_SEED_LABEL
    noise_seed: str = NOISE_SEED_LABEL
    observation_id: str = OBS_ID_LABEL
    pointing_id: str = PNT_ID_LABEL
    observation_time: str = OBS_TIME_LABEL
    tile_id: str = TILE_ID_LABEL

    valid: str = VALID_LABEL


class SheMeasurementsFormat(SheTableFormat):
    """  A class defining the columns common to shear estimates tables. Only the measurements_table_format
         instance of this should generally be accessed, and it should not be changed.
    """

    is_base = True
    unlabelled_columns: List[str]
    meta_type = SheMeasurementsMeta

    def __init__(self,
                 finalize=True):
        super().__init__(finalize=False)

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

        # Shear/shape information (uncalibrated)
        self.e1 = self.set_column_properties(
            "E1", dtype=">f4", fits_dtype="E")
        self.e1_err = self.set_column_properties(
            "E1_ERR", dtype=">f4", fits_dtype="E")
        self.e2 = self.set_column_properties(
            "E2", dtype=">f4", fits_dtype="E")
        self.e2_err = self.set_column_properties(
            "E2_ERR", dtype=">f4", fits_dtype="E")
        self.e_var = self.set_column_properties(
            "E_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.e1e2_covar = self.set_column_properties(
            "E1E2_COVAR", dtype=">f4", fits_dtype="E")

        self.weight = self.set_column_properties(
            "SHEAR_WEIGHT", dtype=">f4", fits_dtype="E")
        self.shape_noise = self.set_column_properties(
            "SHAPE_NOISE", dtype=">f4", fits_dtype="E", is_optional=True)

        # shape information (calibrated)
        self.e1_cal = self.set_column_properties(
            "E1_CAL", dtype=">f4", fits_dtype="E")
        self.e1_cal_err = self.set_column_properties(
            "E1_CAL_ERR", dtype=">f4", fits_dtype="E")
        self.e2_cal = self.set_column_properties(
            "E2_CAL", dtype=">f4", fits_dtype="E")
        self.e2_cal_err = self.set_column_properties(
            "E2_CAL_ERR", dtype=">f4", fits_dtype="E")
        self.e_cal_var = self.set_column_properties(
            "E_CAL_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.e1e2_cal_covar = self.set_column_properties(
            "E1E2_CAL_COVAR", dtype=">f4", fits_dtype="E")
        self.weight_cal = self.set_column_properties(
            "SHEAR_WEIGHT_CAL", dtype=">f4", fits_dtype="E")

        # calibration bias parameters for each object
        self.m11 = self.set_column_properties(
            "M11", dtype=">f4", fits_dtype="E")
        self.m12 = self.set_column_properties(
            "M12", dtype=">f4", fits_dtype="E")
        self.m21 = self.set_column_properties(
            "M21", dtype=">f4", fits_dtype="E")
        self.m22 = self.set_column_properties(
            "M22", dtype=">f4", fits_dtype="E")
        self.c1 = self.set_column_properties(
            "C1", dtype=">f4", fits_dtype="E")
        self.c2 = self.set_column_properties(
            "C2", dtype=">f4", fits_dtype="E")
        self.alpha1 = self.set_column_properties(
            "ALPHA1", dtype=">f4", fits_dtype="E")
        self.alpha2 = self.set_column_properties(
            "ALPHA2", dtype=">f4", fits_dtype="E")

        self.ra = self.set_column_properties(
            "RA", dtype=">f8", fits_dtype="D", comment="deg")
        self.ra_err = self.set_column_properties(
            "RA_ERR", dtype=">f4", fits_dtype="E", comment="deg")
        self.dec = self.set_column_properties(
            "DEC", dtype=">f8", fits_dtype="D", comment="deg")
        self.dec_err = self.set_column_properties(
            "DEC_ERR", dtype=">f4", fits_dtype="E", comment="deg")

        # Information on other galaxy properties

        self.re = self.set_column_properties(
            "RE", dtype=">f4", fits_dtype="E")
        self.re_err = self.set_column_properties(
            "RE_ERR", dtype=">f4", fits_dtype="E")
        self.flux = self.set_column_properties(
            "FLUX", dtype=">f4", fits_dtype="E")
        self.flux_err = self.set_column_properties(
            "FLUX_ERR", dtype=">f4", fits_dtype="E")
        self.magnitude = self.set_column_properties(
            "MAG", dtype=">f4", fits_dtype="E", is_optional=True)
        self.magnitude_err = self.set_column_properties(
            "MAG_ERR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.snr = self.set_column_properties(
            "SNR", dtype=">f4", fits_dtype="E")

        # Other information about observation and tile ID
        # stored on a per object basis as opposed to having it in meta data
        # note on observation id: this is potentially a long string with the list of IDs
        self.tile_ID = self.set_column_properties(
            "TILE_ID", dtype=">i8", fits_dtype="K", is_optional=True)
        self.obs_ID = self.set_column_properties(
            "OBSERVATION_ID", dtype=">i4", fits_dtype="J", is_optional=True, length=4)

        if finalize:
            self._finalize_init()


# Define an instance of this object that can be imported
she_measurements_table_format = SheMeasurementsFormat()

# And a convenient alias for it
tf = she_measurements_table_format
