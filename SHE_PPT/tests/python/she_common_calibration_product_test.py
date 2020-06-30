""" @file common_calibration_product_test.py

    Created 13 Oct 2017

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

__updated__ = "2020-06-22"

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import she_common_calibration as prod


class TestCalibrationParametersProduct(object):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_common_calibration()

        # Check that it validates the schema
        product.validateBinding()

        return

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_common_calibration()

        # Change the fits filenames
        b_filename = "test_file_b.fits"
        product.set_BFD_filename(b_filename)
        k_filename = "test_file_k.fits"
        product.set_KSB_filename(k_filename)
        l_filename = "test_file_l.fits"
        product.set_LensMC_filename(l_filename)
        m_filename = "test_file_m.fits"
        product.set_MomentsML_filename(m_filename)
        r_filename = "test_file_r.fits"
        product.set_REGAUSS_filename(r_filename)

        # Save the product in an XML file
        filename = "she_common_calibration.xml"
        write_xml_product(product, filename, workdir=str(tmpdir))

        # Read back the XML file
        loaded_product = read_xml_product(filename, workdir=str(tmpdir))

        # Check that the filenames match
        assert loaded_product.get_BFD_filename() == "data/" + b_filename
        assert loaded_product.get_KSB_filename() == "data/" + k_filename
        assert loaded_product.get_LensMC_filename() == "data/" + l_filename
        assert loaded_product.get_MomentsML_filename() == "data/" + m_filename
        assert loaded_product.get_REGAUSS_filename() == "data/" + r_filename

        return

    def test_pickle_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_common_calibration()

        # Change the fits filenames
        b_filename = "test_file_b.fits"
        product.set_BFD_filename(b_filename)
        k_filename = "test_file_k.fits"
        product.set_KSB_filename(k_filename)
        l_filename = "test_file_l.fits"
        product.set_LensMC_filename(l_filename)
        m_filename = "test_file_m.fits"
        product.set_MomentsML_filename(m_filename)
        r_filename = "test_file_r.fits"
        product.set_REGAUSS_filename(r_filename)

        # Save the product in a pickled file
        filename = "she_common_calibration.bin"
        write_pickled_product(product, filename, workdir=str(tmpdir))

        # Read back the pickled file
        loaded_product = read_pickled_product(filename, workdir=str(tmpdir))

        # Check that the filenames coincide
        assert loaded_product.get_BFD_filename() == "data/" + b_filename
        assert loaded_product.get_KSB_filename() == "data/" + k_filename
        assert loaded_product.get_LensMC_filename() == "data/" + l_filename
        assert loaded_product.get_MomentsML_filename() == "data/" + m_filename
        assert loaded_product.get_REGAUSS_filename() == "data/" + r_filename

        return
