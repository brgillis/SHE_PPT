""" @file mosaic_product_test.py

    Created 10 Oct 2017

    Unit tests for the mosaic data product.
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

__updated__ = "2019-06-25"

import pytest

from SHE_PPT import detector as dtc
from SHE_PPT.file_io import (read_xml_product, write_xml_product, find_file)
import SHE_PPT.magic_values as mv
from SHE_PPT.products import segmentation_maps as prod
from astropy.io import fits
import numpy as np


class TestStackSegmentationProduct(object):
    """A collection of tests for the stack segmentation data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_stack_reproj_seg_map_data(filename="junk",)

        # Check that it validates the schema
        product.validateBinding()

        pass

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_stack_reproj_seg_map_data(filename="junk",)
        # Change the fits file names
        data_filename = "test_file_data.fits"
        product.set_filename(data_filename)

        # Save the product in an xml file
        write_xml_product(product, "stack_segmentation.xml", workdir=str(tmpdir), allow_pickled=False)

        # Read back the xml file
        loaded_product = read_xml_product("stack_segmentation.xml", workdir=str(tmpdir), allow_pickled=False)

        # Check that it's the same
        assert loaded_product.get_filename() == "data/"+data_filename

        pass

