""" @file simulated_catalog_product_test.py

    Created 17 Nov 2017

    Unit tests for the calibration parameters data product.
"""

# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General
# Public License as published by the Free Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# simulated_catalog.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__updated__ = "2020-10-13"

import pytest

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import she_simulated_catalog as prod


class TestDetailsProduct(object):
    """ ????

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_simulated_catalog()

        # Check that it validates the schema
        product.validateBinding()

        return

    @pytest.mark.skip("No XML implementation yet.")
    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_simulated_catalog()

        # Change the fits filenames
        subfilename = "test_file.fits"
        product.set_data_filename(subfilename)

        # Save the product in an XML file
        filename = "she_simulated_catalog.xml"
        write_xml_product(product, filename, workdir=str(tmpdir))

        # Read back the XML file
        loaded_product = read_xml_product(filename, workdir=str(tmpdir))

        # Check that the filenames match
        assert loaded_product.get_data_filename() == "data/" + subfilename

        return

    def test_pickle_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_simulated_catalog()

        # Change the fits filenames
        subfilename = "test_file.fits"
        product.set_data_filename(subfilename)

        # Save the product in an XML file
        filename = "she_simulated_catalog.xml"
        write_pickled_product(product, filename, workdir=str(tmpdir))

        # Read back the XML file
        loaded_product = read_pickled_product(filename, workdir=str(tmpdir))

        # Check that the filenames match
        assert loaded_product.get_data_filename() == "data/" + subfilename

        return
