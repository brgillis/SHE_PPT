""" @file she_validation_test_results_product_test.py

    Created 24 Nov 2020

    Unit tests for the she_validation_test_results data product.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__updated__ = "2020-11-24"

import os
import pytest

from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products import she_validation_test_results as prod


class TestValidationTestResults(object):
    """A collection of tests for the she_validation_test_results data product.

    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        return

    @classmethod
    def setup_class(cls):
        return

    @classmethod
    def teardown_class(cls):
        return

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_validation_test_results()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self):

        # Create the product
        product = prod.create_dpd_she_validation_test_results()

        # Save the product in an xml file
        write_xml_product(product, self.filename, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename, workdir=self.workdir)

        # Check that it's the same
        # TODO: Add some test here

        return
