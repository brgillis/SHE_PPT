""" @file simulation_plan.py

    Created 29 Nov 2017

    Format definition for a table outlining a simulation plan.
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


from ..constants.fits import FITS_VERSION_LABEL, FITS_DEF_LABEL, EXTNAME_LABEL
from ..table_utility import is_in_format, init_table,SheTableFormat


fits_version = "8.0"
fits_def = "she.simulationPlan"


class SheSimulationPlanMeta():
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    def __init__(self):

        self.__version__ = fits_version
        self.table_format = fits_def

        # Table metadata labels
        self.fits_version = FITS_VERSION_LABEL
        self.fits_def = FITS_DEF_LABEL

        # Store the less-used comments in a dict
        self.comments = OrderedDict(((self.fits_version, None),
                                     (self.fits_def, None),
                                     ))

        # A list of columns in the desired order
        self.all = list(self.comments.keys())


class SheSimulationPlanFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the simulation_plan_table_format
               instance of this should generally be accessed, and it should not be changed.
    """

    def __init__(self):
        super().__init__(SheSimulationPlanMeta())

        # Column names and info

        self.tag = self.set_column_properties("TAG", dtype="str", fits_dtype="10A", length=10,
                                         comment="Tag to be added to file names for this batch, max length 10.")

        self.model_seed_min = self.set_column_properties("MSEED_MIN", dtype=">i8", fits_dtype="K",
                                                    comment="Minimum model seed value for this batch.")
        self.model_seed_max = self.set_column_properties("MSEED_MAX", dtype=">i8", fits_dtype="K",
                                                    comment="Maximum model seed value for this batch.")
        self.model_seed_step = self.set_column_properties("MSEED_STEP", dtype=">i8", fits_dtype="K",
                                                     comment="Model seed step for this batch.")

        self.noise_seed_min = self.set_column_properties("NSEED_MIN", dtype=">i8", fits_dtype="K",
                                                    comment="Minimum model seed value for this batch.")
        self.noise_seed_max = self.set_column_properties("NSEED_MAX", dtype=">i8", fits_dtype="K",
                                                    comment="Maximum model seed value for this batch.")
        self.noise_seed_step = self.set_column_properties("NSEED_STEP", dtype=">i8", fits_dtype="K",
                                                     comment="Model seed step for this batch.")

        self.suppress_noise = self.set_column_properties(
                                                    "SUP_NOISE", dtype="bool", fits_dtype="L")
        self.num_detectors = self.set_column_properties(
                                                   "NUM_DETECTORS", dtype=">i2", fits_dtype="I")
        self.num_galaxies = self.set_column_properties(
                                                  "NUM_GALAXIES", dtype=">i2", fits_dtype="I")
        self.render_background = self.set_column_properties(
                                                       "RENDER_BKG", dtype="bool", fits_dtype="L")

        self._finalize_init()


# Define an instance of this object that can be imported
simulation_plan_table_format = SheSimulationPlanFormat()

# And a convient alias for it
tf = simulation_plan_table_format


def make_simulation_plan_table_header():
    """
        @brief Generate a header for a galaxy population table.

        @return header <OrderedDict>
    """

    header = OrderedDict()

    header[tf.m.fits_version] = tf.__version__
    header[tf.m.fits_def] = fits_def

    return header


def initialise_simulation_plan_table(size=None,
                                     optional_columns=None,
                                     init_cols=None,):
    """
        @brief Initialise a galaxy population table.

        @return simulation_plan_table <astropy.Table>
    """

    if optional_columns is None:
        optional_columns = []
    else:
        # Check all optional columns are valid
        for colname in optional_columns:
            if colname not in tf.all:
                raise ValueError("Invalid optional column name: " + colname)

    simulation_plan_table = init_table(tf, optional_columns=optional_columns, init_cols=init_cols, size=size)

    simulation_plan_table.meta = make_simulation_plan_table_header()

    assert is_in_format(simulation_plan_table, tf)

    return simulation_plan_table
