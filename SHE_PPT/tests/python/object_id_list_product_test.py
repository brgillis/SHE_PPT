""" @file object_id_list_product_test.py

    Created 14 Mar 2019

    Unit tests for the object_id_list data product.
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

__updated__ = "2019-06-24"

import os
import pytest

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import object_id_list as prod


class TestObjectIdList(object):
    """A collection of tests for the object_id_list data product.

    """

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.workdir = tmpdir.strpath
        return

    @classmethod
    def setup_class(cls):
        cls.ex_ids = [12, 14]
        cls.filename = "she_object_id_list.bin"
        return

    @classmethod
    def teardown_class(cls):
        del cls.ex_ids
        return

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_object_id_list()

        # Check that it validates the schema
        product.validateBinding()

        pass

    @pytest.mark.skip(reason="XML definition not yet available")
    def test_xml_writing_and_reading(self):

        # Create the product
        product = prod.create_dpd_she_object_id_list(self.ex_ids)

        # Save the product in an xml file
        write_xml_product(product, self.filename, workdir=self.workdir, allow_pickled=False)

        # Read back the xml file
        loaded_product = read_xml_product(self.filename, workdir=self.workdir, allow_pickled=False)

        # Check that it's the same
        assert loaded_product.get_id_list() == product.get_id_list()

        return

    def test_pickle_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_object_id_list(self.ex_ids)

        # Save the product in an xml file
        write_pickled_product(product, self.filename, workdir=self.workdir)

        # Read back the pickled file
        loaded_product = read_pickled_product(self.filename, workdir=self.workdir)

        # Check that it's the same
        assert loaded_product.get_id_list() == product.get_id_list()

        return
