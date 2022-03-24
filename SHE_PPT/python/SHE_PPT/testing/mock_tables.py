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
import os
from typing import Callable, Dict, Optional, Sequence, Type, TypeVar

import numpy as np
from astropy.table import Table

from SHE_PPT.file_io import DEFAULT_WORKDIR, try_remove_file, write_listfile, write_product_and_table, write_table
from SHE_PPT.logging import getLogger
from SHE_PPT.table_utility import SheTableFormat
from SHE_PPT.testing.mock_data import MockDataGenerator, NUM_TEST_POINTS
from SHE_PPT.utility import default_value_if_none, empty_list_if_none

logger = getLogger(__name__)

MockDataGeneratorType = TypeVar('MockDataGeneratorType', bound = MockDataGenerator)

DEFAULT_TABLE_FILENAME = "table.fits"
DEFAULT_PRODUCT_FILENAME = "product.xml"
DEFAULT_LISTFILE_FILENAME = "listfile.json"


class MockTableGenerator:
    """ A class to handle the generation of a mock table from mock data.
    """

    # Class-level attributes
    mock_data_generator_type: Type[MockDataGeneratorType] = MockDataGenerator
    product_creator: Optional[Callable] = None

    # Attributes optionally set at init or with defaults
    mock_data_generator: Optional[MockDataGeneratorType] = None
    tf: Optional[SheTableFormat] = None
    optional_columns: Sequence[str]
    seed: int = 1
    num_test_points: int = NUM_TEST_POINTS
    table_filename: str = DEFAULT_TABLE_FILENAME
    product_filename: str = DEFAULT_PRODUCT_FILENAME
    listfile_filename: str = DEFAULT_LISTFILE_FILENAME
    workdir: str = DEFAULT_WORKDIR

    # Attributes set when table is generated.
    _mock_table: Optional[Table] = None

    @property
    def mock_table(self):
        if self._mock_table is None:
            self.mock_data_generator.generate_data()
            self._make_mock_table()
        return self._mock_table

    def __init__(self,
                 mock_data_generator: Optional[MockDataGeneratorType] = None,
                 tf: Optional[SheTableFormat] = None,
                 optional_columns: Optional[Sequence[str]] = None,
                 seed: Optional[int] = None,
                 num_test_points: Optional[int] = None,
                 table_filename: Optional[str] = None,
                 product_filename: Optional[str] = None,
                 listfile_filename: Optional[str] = None,
                 workdir: Optional[str] = None, ) -> None:
        """ Initializes the class.
        """

        # Init values, using defaults if not provided
        self.tf = default_value_if_none(x = tf, default_x = self.tf)

        self.optional_columns = empty_list_if_none(optional_columns, coerce = True)

        self.seed = default_value_if_none(x = seed, default_x = self.seed)
        self.num_test_points = default_value_if_none(x = num_test_points, default_x = self.num_test_points)

        self.table_filename = default_value_if_none(x = table_filename, default_x = self.table_filename)
        self.product_filename = default_value_if_none(x = product_filename, default_x = self.product_filename)
        self.listfile_filename = default_value_if_none(x = listfile_filename, default_x = self.listfile_filename)

        self.workdir = default_value_if_none(x = workdir, default_x = self.workdir)

        # We don't use default_value_if_none here to avoid unnecessarily generating the data
        if mock_data_generator is None:
            self.mock_data_generator = self.mock_data_generator_type(tf = self.tf,
                                                                     num_test_points = num_test_points,
                                                                     seed = self.seed)
        else:
            self.mock_data_generator = mock_data_generator

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
        return self.mock_table

    def write_mock_table(self) -> str:
        """ Generates a mock table if necessary, and writes it out.

            Returns workdir-relative filename of the written-out table.
        """

        write_table(t = self.mock_table,
                    filename = self.table_filename,
                    workdir = self.workdir)

        return self.table_filename

    def write_mock_product(self) -> str:
        """ Generates a mock table if necessary, and writes it out, as well as a data product containing it.

            Returns workdir-relative filename of the written-out data product.
        """

        if self.product_creator is None:
            raise TypeError("write_mock_product can only be called if self.product_creator is set to a creation"
                            "function for the desired type of product to be written")

        write_product_and_table(product = self.product_creator(),
                                product_filename = self.product_filename,
                                table = self.mock_table,
                                table_filename = self.table_filename)

        return self.product_filename

    def write_mock_listfile(self) -> str:

        if self.product_creator is None:
            raise TypeError("write_mock_listfile can only be called if self.product_type is set to the desired type of "
                            "product to be written")

        # Write the product first, then write it in a listfile
        self.write_mock_product()
        write_listfile(os.path.join(self.workdir, self.listfile_filename), [self.product_filename])

        return self.listfile_filename

    def cleanup(self):
        """ To be called in cleanup, deletes any table, product, and/or listfile which has been written out
        """

        try_remove_file(self.table_filename, workdir = self.workdir)
        try_remove_file(self.product_filename, workdir = self.workdir)
        try_remove_file(self.listfile_filename, workdir = self.workdir)
