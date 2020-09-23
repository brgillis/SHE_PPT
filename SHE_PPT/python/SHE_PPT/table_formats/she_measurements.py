""" @file she_measurements.py

    Created 2020-07-03

    Base format definition for common properties of all shear measurements tables.
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

__updated__ = "2020-09-23"

from collections import OrderedDict

from astropy.table import Table

from SHE_PPT import magic_values as mv
from SHE_PPT.flags import she_flag_version
from SHE_PPT.table_utility import setup_table_format, set_column_properties

fits_version = "8.0"
fits_def = "she.measurements"


class SheMeasurementsMeta(object):
    """
        @brief A class defining the metadata for shear estimates tables.
    """

    def __init__(self):

        self.table_format = fits_def
        self.__version__ = fits_version

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

        self.valid = mv.valid_label

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     (self.she_flag_version, None),
                                     (self.model_hash, None),
                                     (self.model_seed, None),
                                     (self.noise_seed, None),
                                     (self.observation_id, None),
                                     (self.observation_time, None),
                                     (self.tile_id, None),
                                     (self.valid,
                                      "0: Not tested; 1: Pass; -1: Fail")
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheMeasurementsFormat(object):
    """
        @brief A class defining the format for shear estimates tables. Only the measurements_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):

        # Get the metadata (contained within its own class)
        self.meta = SheMeasurementsMeta()

        setup_table_format(self)

        self.is_base = True

        # Table column labels and properties

        self.ID = set_column_properties(self,
                                        "OBJECT_ID", dtype=">i8", fits_dtype="K")

        self.fit_flags = set_column_properties(self,
                                               "FIT_FLAGS", dtype=">i8", fits_dtype="K")
        self.val_flags = set_column_properties(self,
                                               "VAL_FLAGS", dtype=">i8", fits_dtype="K")
        self.fit_class = set_column_properties(self,
                                               "FIT_CLASS", dtype=">i2", fits_dtype="I")

        self.g1 = set_column_properties(self,
                                        "G1", dtype=">f4", fits_dtype="E")
        self.g1_err = set_column_properties(self,
                                            "G1_ERR", dtype=">f4", fits_dtype="E")
        self.g2 = set_column_properties(self,
                                        "G2", dtype=">f4", fits_dtype="E")
        self.g2_err = set_column_properties(self,
                                            "G2_ERR", dtype=">f4", fits_dtype="E")
        self.e_var = set_column_properties(self,
                                           "E_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1g2_covar = set_column_properties(self,
                                                "G1G2_COVAR", dtype=">f4", fits_dtype="E")
        self.weight = set_column_properties(self,
                                            "SHEAR_WEIGHT", dtype=">f4", fits_dtype="E")
        self.shape_weight = set_column_properties(self,
                                                  "SHAPE_WEIGHT", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1_uncal = set_column_properties(self,
                                              "G1_UNCAL", dtype=">f4", fits_dtype="E")
        self.g1_uncal_err = set_column_properties(self,
                                                  "G1_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.g2_uncal = set_column_properties(self,
                                              "G2_UNCAL", dtype=">f4", fits_dtype="E")
        self.g2_uncal_err = set_column_properties(self,
                                                  "G2_UNCAL_ERR", dtype=">f4", fits_dtype="E")
        self.e_uncal_var = set_column_properties(self,
                                                 "E_UNCAL_VAR", dtype=">f4", fits_dtype="E", is_optional=True)
        self.g1g2_uncal_covar = set_column_properties(self,
                                                      "G1G2_UNCAL_COVAR", dtype=">f4", fits_dtype="E")
        self.weight_uncal = set_column_properties(self,
                                                  "SHEAR_WEIGHT_UNCAL", dtype=">f4", fits_dtype="E")
        self.shape_weight_uncal = set_column_properties(self,
                                                        "SHAPE_WEIGHT_UNCAL", dtype=">f4", fits_dtype="E", is_optional=True)
        self.shape_noise = set_column_properties(self,
                                                 "ASSUMED_SHAPE_NOISE", dtype=">f4", fits_dtype="E", is_optional=True)

        self.ra = set_column_properties(self,
                                        "UPDATED_RA", comment="deg")
        self.ra_err = set_column_properties(self,
                                            "UPDATED_RA_ERR", comment="deg")
        self.dec = set_column_properties(self,
                                         "UPDATED_DEC", comment="deg")
        self.dec_err = set_column_properties(self,
                                             "UPDATED_DEC_ERR", comment="deg")

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
she_measurements_table_format = SheMeasurementsFormat()

# And a convient alias for it
tf = she_measurements_table_format
