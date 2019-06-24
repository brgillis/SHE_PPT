""" @file calibrated_frame_product_test.py

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

__updated__ = "2019-06-24"

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import calibrated_frame as prod


class TestCalibratedFrameProduct(object):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):

        # Create the product
        subfilename = "foo.fits"
        product = prod.create_dpd_vis_calibrated_frame(data_filename=subfilename)

        # Check that it validates the schema
        product.validateBinding()

        # Check that it was inited with the proper filename
        assert product.get_data_filename() == subfilename

        pass

    def test_default_filenames(self):
        """Test that all filenames in a default product are empty.
        """

        prod.init()

        product = prod.create_dpd_vis_calibrated_frame()

        for filename in product.get_all_filenames():
            assert filename == "" or filename is None

        return

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_vis_calibrated_frame()

        # Change the fits filenames
        sub_data_filename = "test_data_file.fits"
        product.set_data_filename(sub_data_filename)
        sub_psf_filename = "test_psf_file.fits"
        product.set_psf_filename(sub_psf_filename)
        sub_wgt_filename = "test_wgt_file.fits"
        product.set_wgt_filename(sub_wgt_filename)
        sub_bkg_filename = "test_bkg_file.fits"
        product.set_bkg_filename(sub_bkg_filename)

        # Save the product in an XML file
        write_xml_product(product, vis_calibrated_frame.xml, workdir=str(tmpdir), allow_pickled=False)

        # Read back the XML file
        loaded_product = read_xml_product(filename, allow_pickled=False)

        # Check that the filenames match
        assert loaded_product.get_data_filename() == sub_data_filename
        assert loaded_product.get_psf_filename() == sub_psf_filename
        assert loaded_product.get_wgt_filename() == sub_wgt_filename
        assert loaded_product.get_bkg_filename() == sub_bkg_filename

        pass
