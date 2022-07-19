""" @file she_tu_matched.py

    Created 2021/08/10

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

from .she_measurements import SheMeasurementsFormat
from ..constants.fits import (MODEL_HASH_LABEL, MODEL_SEED_LABEL, NOISE_SEED_LABEL, OBS_ID_LABEL, OBS_TIME_LABEL,
                              PNT_ID_LABEL, SHE_FLAG_VERSION_LABEL, TILE_ID_LABEL, VALID_LABEL, )
from ..table_utility import SheTableMeta

fits_version = "8.0"
fits_def = "she.tu_matched_cat"


class SheTUMatchedMeta(SheTableMeta):
    """ A class defining the metadata common to shear TU matched tables
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    she_flag_version: str = SHE_FLAG_VERSION_LABEL
    model_hash: str = MODEL_HASH_LABEL
    model_seed: str = MODEL_SEED_LABEL
    noise_seed: str = NOISE_SEED_LABEL
    observation_id: str = OBS_ID_LABEL
    pointing_id: str = PNT_ID_LABEL
    observation_time: str = OBS_TIME_LABEL
    tile_id: str = TILE_ID_LABEL

    valid: str = VALID_LABEL

    def __init__(self):
        super().__init__(comments=OrderedDict(((self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.she_flag_version, None),
                                               (self.model_hash, None),
                                               (self.model_seed, None),
                                               (self.noise_seed, None),
                                               (self.observation_id, "Individual ID or list of IDs"),
                                               (self.pointing_id, "List of pointing IDs"),
                                               (self.observation_time, "Individual time or list of times"),
                                               (self.tile_id, "Individual ID or list of IDs"),
                                               (self.valid, "0: Not tested; 1: Pass; -1: Fail")
                                               )))


class SheTUMatchedFormat(SheMeasurementsFormat):
    """ A class defining the columns common to shear tu matched tables. This inherits from SheMeasurementsFormat,
        to include all the columns in it.
    """

    # Define this as a base class
    is_base: bool = True

    meta_type = SheTUMatchedMeta

    def __init__(self,
                 finalize: bool = True):

        super().__init__(finalize=False)

        # Table column labels and properties unique to this table, from the TU Galaxy table
        self.tu_ra = self.set_column_properties("RA_MAG", fits_dtype="E", dtype=">f4", comment="",
                                                unlabelled=True)
        self.tu_dec = self.set_column_properties("DEC_MAG", fits_dtype="E", dtype=">f4", comment="",
                                                 unlabelled=True)
        self.tu_gamma1 = self.set_column_properties("GAMMA1", fits_dtype="E", dtype=">f4", comment="",
                                                    unlabelled=True)
        self.tu_gamma2 = self.set_column_properties("GAMMA2", fits_dtype="E", dtype=">f4", comment="",
                                                    unlabelled=True)
        self.tu_kappa = self.set_column_properties("KAPPA", fits_dtype="E", dtype=">f4", comment="",
                                                   unlabelled=True)
        self.tu_disk_angle = self.set_column_properties("DISK_ANGLE", fits_dtype="E",
                                                        dtype=">f4", comment="", unlabelled=True)
        self.tu_disk_axis_ratio = self.set_column_properties("DISK_AXIS_RATIO", fits_dtype="E",
                                                             dtype=">f4", comment="", unlabelled=True)

        # Column labels for summary galaxy properties calculated from the TU Galaxy table
        self.tu_gal_index = self.set_column_properties("GAL_INDEX", fits_dtype="E", dtype=">f4",
                                                       comment="", unlabelled=True, is_optional=True)
        self.tu_star_index = self.set_column_properties("STAR_INDEX", fits_dtype="E", dtype=">f4",
                                                        comment="", unlabelled=True, is_optional=True)
        self.tu_g_beta = self.set_column_properties("Beta_Input_Shear", fits_dtype="E", dtype=">f4",
                                                    comment="", unlabelled=True, is_optional=True)
        self.tu_g_mag = self.set_column_properties("Mag_Input_Shear", fits_dtype="E", dtype=">f4",
                                                   comment="", unlabelled=True, is_optional=True)
        self.tu_bulge_beta = self.set_column_properties("Beta_Input_Bulge_Unsheared_Shape", fits_dtype="E",
                                                        dtype=">f4", comment="", unlabelled=True,
                                                        is_optional=True)
        self.tu_disk_beta = self.set_column_properties("Beta_Input_Disk_Unsheared_Shape", fits_dtype="E",
                                                       dtype=">f4", comment="", unlabelled=True,
                                                       is_optional=True)

        # Column labels for summary galaxy properties calculated from measurements tables
        self.g_beta = self.set_column_properties("Beta_Est_Shear", fits_dtype="E", dtype=">f4",
                                                 comment="", unlabelled=False, is_optional=True)
        self.g_mag = self.set_column_properties("Mag_Est_Shear", fits_dtype="E",
                                                dtype=">f4", comment="", unlabelled=False, is_optional=True)

        # Column labels for properties that are binned on in validation tests
        # SNR is already defined in measurements table
        self.colour = self.set_column_properties("COLOUR", is_optional=True)
        self.size = self.set_column_properties("SIZE", is_optional=True)
        self.bg = self.set_column_properties("BG", is_optional=True)
        self.epoch = self.set_column_properties("EPOCH", is_optional=True)

        if finalize:
            self._finalize_init()


# Define an instance of this object that can be imported
she_tu_matched_table_format = SheTUMatchedFormat()

# And a convenient alias for it
tf = she_tu_matched_table_format
