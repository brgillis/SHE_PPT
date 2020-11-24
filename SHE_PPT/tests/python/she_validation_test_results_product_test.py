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

        cls.filename = "she_validation_test_results.xml"
        cls.filename_zero = "she_validation_test_results_0.xml"
        cls.filename_three = "she_validation_test_results_3.xml"

        cls.source_pipeline = "sheReconciliation"
        cls.observation_mode = "ScienceDeep"
        cls.num_exposures = 3

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
        product = prod.create_dpd_she_validation_test_results(source_pipeline=self.source_pipeline,
                                                              observation_mode=self.observation_mode,
                                                              num_exposures=self.num_exposures)

        # Save the product in an xml file
        write_xml_product(product, self.filename, workdir=self.workdir)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename, workdir=self.workdir)

        # Check that it's the same
        assert loaded_product.Data.SourcePipeline == self.source_pipeline
        assert loaded_product.Data.ObservationMode == self.observation_mode
        assert loaded_product.Data.NumberExposures == self.num_exposures

        # Try with zero and multiple tests

        # Create the product
        product_zero = prod.create_dpd_she_validation_test_results(num_tests=0)

        # Save the product in an xml file
        write_xml_product(product_zero, self.filename_zero, workdir=self.workdir)

        # Read back the xml file
        loaded_product_zero = read_xml_product(self.filename_zero, workdir=self.workdir)

        assert len(loaded_product_zero.Data.ValidationTestList) == 0

        # Create the product
        product_three = prod.create_dpd_she_validation_test_results(num_tests=3)

        # Save the product in an xml file
        write_xml_product(product_three, self.filename_zero, workdir=self.workdir)

        # Read back the xml file
        loaded_product_three = read_xml_product(self.filename_zero, workdir=self.workdir)

        assert len(loaded_product_three.Data.ValidationTestList) == 3

        return
