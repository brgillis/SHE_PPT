""" @file she_psf_calibration_parameters_product_test.py

    Created 10 Oct 2017

    Unit tests for the she_psf_calibration_parameters data product.
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
from SHE_PPT.products import she_psf_calibration_parameters as prod


class TestPSFCalibrationProduct(object):
    """A collection of tests for the she_psf_calibration_parameters data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_psf_calibration_parameters()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_psf_calibration_parameters()

        # Change the fits file names
        data_filename = "test_file.fits"
        product.set_data_filename(data_filename)

        # Save the product in an xml file
        filename = "she_psf_calibration_parameters.xml"
        write_xml_product(product, filename, workdir=str(tmpdir))

        # Read back the xml file
        loaded_product = read_xml_product(filename, workdir=str(tmpdir))

        # Check that it's the same
        assert loaded_product.get_data_filename() == "data/" + data_filename

        return
