""" @file le1_aocs_time_series_product_test.py

    Created 10 Oct 2017

    Unit tests for the le1_aocs_time_series data product.
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

__updated__ = "2020-10-15"

from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products import le1_aocs_time_series as prod


class TestAocsTimeSeriesProduct(object):
    """A collection of tests for the aocs_time_series data product.

    """

    def test_validation(self):
        # Create the product
        product = prod.create_dpd_le1_aocs_time_series()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self, tmpdir):
        # Create the product
        product = prod.create_dpd_le1_aocs_time_series()

        # TODO Change something about it here when there's something to be changed

        # Save the product in an xml file
        file_name = tmpdir.join("she_aocs_time_series.xml")
        write_xml_product(product, file_name)

        # Read back the xml file
        loaded_product = read_xml_product(file_name)

        # Check that it's the same
        assert (loaded_product.get_filename() == product.get_filename())

        return
