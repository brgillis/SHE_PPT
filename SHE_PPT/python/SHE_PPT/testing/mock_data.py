""" @file mock_data.py

    Created 15 October 2021.

    Utilities to generate mock data for validation tests.
"""

__updated__ = "2021-10-05"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

from abc import ABC, abstractmethod
from typing import Dict, Optional

import numpy as np

from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat
from SHE_PPT.utility import default_value_if_none

logger = getLogger(__name__)

# General info about the data
NUM_GOOD_TEST_POINTS = 32
NUM_NAN_TEST_POINTS = 2
NUM_ZERO_WEIGHT_TEST_POINTS = 1
NUM_TEST_POINTS = NUM_GOOD_TEST_POINTS + NUM_NAN_TEST_POINTS + NUM_ZERO_WEIGHT_TEST_POINTS


class MockDataGenerator(ABC):
    """ A class to handle the generation of mock data for testing.
    """

    # Attributes optionally set at init or with defaults
    tf: Optional[SheTableFormat] = None
    num_test_points: int = NUM_TEST_POINTS
    seed: int = 0

    # Attributes set when data is generated
    data: Optional[Dict[str, np.ndarray]] = None

    def __init__(self,
                 tf: Optional[SheTableFormat] = None,
                 num_test_points: Optional[int] = None,
                 seed: Optional[int] = None) -> None:
        """ Initializes the class.
        """
        self.tf = default_value_if_none(x = tf,
                                        default_x = self.tf)
        self.num_test_points = default_value_if_none(x = num_test_points,
                                                     default_x = self.num_test_points)
        self.seed = default_value_if_none(x = seed,
                                          default_x = self.seed)

    def _generate_base_data(self):
        """ Set up base data which is commonly used.
        """
        self._indices = np.indices((self.num_test_points,), dtype = int, )[0]
        self._zeros = np.zeros(self.num_test_points, dtype = '>f4')
        self._ones = np.ones(self.num_test_points, dtype = '>f4')

        self.data = {}

    def _seed_rng(self):
        """Seed the random number generator
        """
        self._rng = np.random.default_rng(self.seed)

    def get_data(self):
        """ Get the data, generating if needed.
        """
        if self.data is None:
            self.generate_data()
        return self.data

    def generate_data(self):
        """ Generates data based on input parameters.
        """

        # Generate generic data first
        self._seed_rng()
        self._generate_base_data()

        # Call the abstract method to generate unique data for each type
        self._generate_unique_data()

    @abstractmethod
    def _generate_unique_data(self):
        """ Generates data unique to this type.
        """
