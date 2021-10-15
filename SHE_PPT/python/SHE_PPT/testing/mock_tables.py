""" @file mock_tables.py

    Created 15 October 2021.

    Utilities to generate mock tables for validation tests.
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
from typing import Dict, Optional, Sequence

import numpy as np
from astropy.table import Table

from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat
from SHE_PPT.testing.mock_data import MockDataGenerator
from SHE_PPT.utility import default_value_if_none, empty_list_if_none

logger = getLogger(__name__)


class MockTableGenerator:
    """ A class to handle the generation of a mock table from mock data.
    """

    # Attributes set at init
    mock_data_generator: MockDataGenerator

    # Attributes optionally set at init or with defaults
    tf: Optional[SheTableFormat] = None
    optional_columns: Sequence[str]

    # Attributes set when table is generated.
    _mock_table: Optional[Table] = None

    def __init__(self,
                 mock_data_generator: MockDataGenerator,
                 tf: Optional[SheTableFormat] = None,
                 optional_columns: Optional[Sequence[str]] = None) -> None:
        """ Initializes the class.
        """
        self.mock_data_generator = mock_data_generator
        self.tf = default_value_if_none(x = tf, default_x = self.tf)
        self.optional_columns = empty_list_if_none(optional_columns, coerce = True)

    def _make_mock_table(self) -> None:
        """ Method to generate the mock table, filling in self._mock_table with a Table of the desired format. Can
            be overridden by subclasses to alter the table after creation.
        """

        # If the Table format is none, raise an exception
        if self.tf is None:
            raise ValueError("Mock table cannot be generated if table format (tf) is None.")

        # Init with just the size, to avoid irrelevant errors about wrong datatypes
        self._mock_table = self.tf.init_table(size = self.mock_data_generator.num_test_points)

        # Fill in the data
        data: Dict[str, np.ndarray] = self.mock_data_generator.data
        for colname in data:
            self._mock_table[colname] = data[colname]

    def get_mock_table(self) -> Table:
        """ Gets the generated mock table.
        """
        if self._mock_table is None:
            self.mock_data_generator.generate_data()
            self._make_mock_table()
        return self._mock_table
