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

__updated__ = "2021-08-12"

from ..constants.fits import FITS_DEF_LABEL, FITS_VERSION_LABEL
from ..table_utility import SheTableFormat, SheTableMeta

fits_version = "8.0"
fits_def = "she.simulationPlan"


class SheSimulationPlanMeta(SheTableMeta):
    """
        @brief A class defining the metadata for simulation plan tables.
    """

    __version__: str = fits_version
    table_format: str = fits_def

    # Table metadata labels
    fits_version: str = FITS_VERSION_LABEL
    fits_def: str = FITS_DEF_LABEL


class SheSimulationPlanFormat(SheTableFormat):
    """
        @brief A class defining the format for galaxy population priors tables. Only the simulation_plan_table_format
               instance of this should generally be accessed, and it should not be changed.
    """
    meta_type = SheSimulationPlanMeta

    def __init__(self):
        super().__init__()

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

# And a convenient alias for it
tf = simulation_plan_table_format
