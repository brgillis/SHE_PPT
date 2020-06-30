""" @file she_psf_field_parameters_product_test.py

    Created 10 Oct 2017

    Unit tests for the she_psf_field_parameters data product.
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

__updated__ = "2020-06-25"

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import she_psf_field_parameters as prod


class TestPSFCalibrationProduct(object):
    """A collection of tests for the she_psf_field_parameters data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_psf_field_parameters()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_psf_field_parameters()

        # Change the fits file names
        zm_filename = "test_file_zm.fits"
        product.set_zernike_mode_filename(zm_filename)
        se_filename = "test_file_se.fits"
        product.set_surface_error_filename(se_filename)

        # Save the product in an xml file
        filename = "she_psf_field_parameters.xml"
        write_xml_product(product, filename, workdir=str(tmpdir))

        # Read back the xml file
        loaded_product = read_xml_product(filename, workdir=str(tmpdir))

        # Check that it's the same
        assert loaded_product.get_zernike_mode_filename() == "data/" + zm_filename
        assert loaded_product.get_surface_error_filename() == "data/" + se_filename

        return

    def test_pickle_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_psf_field_parameters()

        # Change the fits file names
        zm_filename = "test_file_zm.fits"
        product.set_zernike_mode_filename(zm_filename)
        se_filename = "test_file_se.fits"
        product.set_surface_error_filename(se_filename)

        # Save the product in a pickled file
        filename = "she_psf_field_parameters.bin"
        write_pickled_product(product, filename, workdir=str(tmpdir))

        # Read back the pickled file
        loaded_product = read_pickled_product(filename, workdir=str(tmpdir))

        # Check that it's the same
        assert loaded_product.get_zernike_mode_filename() == "data/" + zm_filename
        assert loaded_product.get_surface_error_filename() == "data/" + se_filename

        return
