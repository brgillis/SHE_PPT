""" @file she_tu_matched_cat.py

    Created 2021/08/10

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

__updated__ = "2021-08-10"

from collections import OrderedDict

from .. import magic_values as mv
from ..table_utility import SheTableMeta
from .she_measurements import SheMeasurementsFormat


fits_version = "8.0"
fits_def = "she.tu_matched_cat"


class SheTUMatchedCatMeta(SheTableMeta):
    """ A class defining the metadata common to shear TU matched tables
    """

    def __init__(self):

        # Table metadata labels
        self.fits_version = mv.fits_version_label
        self.fits_def = mv.fits_def_label
        self.she_flag_version = mv.she_flag_version_label
        self.model_hash = mv.model_hash_label
        self.model_seed = mv.model_seed_label
        self.noise_seed = mv.noise_seed_label
        self.observation_id = mv.obs_id_label
        self.pointing_id = mv.pnt_id_label
        self.observation_time = mv.obs_time_label
        self.tile_id = mv.tile_id_label

        self.valid = mv.valid_label

        super().__init__(table_format=fits_def,
                         version=fits_version,
                         comments=OrderedDict(((self.fits_version, None),
                                               (self.fits_def, None),
                                               (self.she_flag_version, None),
                                               (self.model_hash, None),
                                               (self.model_seed, None),
                                               (self.noise_seed, None),
                                               (self.observation_id, "Individual ID or list of IDs"),
                                               (self.pointing_id, "List of pointing IDs"),
                                               (self.observation_time, "Individual time or list of times"),
                                               (self.tile_id, "Individual ID or list of IDs"),
                                               (self.valid,  "0: Not tested; 1: Pass; -1: Fail")
                                               )))


class SheTUMatchedCatFormat(SheMeasurementsFormat):
    """ A class defining the columns common to shear tu matched tables. This inherits from SheMeasurementsFormat,
        to include all the columns in it.
    """

    # Define this as a base class
    is_base: bool = True

    def __init__(self, meta=None):
        if meta is None:
            meta = SheTUMatchedCatMeta()
        super().__init__(meta)

        # Table column labels and properties unique to this table

        # A list of columns in the desired order
        self.all = list(self.is_optional.keys())

        # A list of required columns in the desired order
        self.all_required = []
        for label in self.all:
            if not self.is_optional[label]:
                self.all_required.append(label)


# Define an instance of this object that can be imported
she_tu_matched_cat_table_format = SheTUMatchedCatFormat()

# And a convenient alias for it
tf = she_tu_matched_cat_table_format
