""" @file vis_stacked_frame_product_test.py

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
# details.
#
# You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__updated__ = "2020-10-15"

from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products import vis_stacked_frame as prod
from SHE_PPT.testing.utility import SheTestCase


class TestStackedFrameProduct(SheTestCase):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):
        # Create the product
        product = prod.create_dpd_vis_stacked_frame()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self, tmpdir):
        # Create the product
        product = prod.create_dpd_vis_stacked_frame()

        # Change the fits filenames
        subfilename = "test_file.fits"
        product.set_data_filename(subfilename)

        # Save the product in an XML file
        write_xml_product(product, "she_stacked_frame.xml", workdir=str(tmpdir))

        # Read back the XML file
        loaded_product = read_xml_product("she_stacked_frame.xml", workdir=str(tmpdir))

        # Check that the filenames match
        assert loaded_product.get_data_filename() == "data/" + subfilename

        return
