""" @file shear_estimates_product_test.py

    Created 9 Oct 2017

    Unit tests for the shear estimates data product.
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

from SHE_PPT.products import shear_estimates as prod
from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)

class TestShearEstimatesProduct(object):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_shear_estimates()

        # Check that it validates the schema
        product.validateBinding()

        pass

    def test_xml_writing_and_reading(self, tmpdir):

        prod.init()

        # Create the product
        product = prod.create_dpd_shear_estimates()

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
        filename = tmpdir.join("she_shear_estimates.xml")
        write_xml_product(product, filename)

        # Read back the XML file
        loaded_product = read_xml_product(filename)

        # Check that the filenames coincide
        assert loaded_product.get_BFD_filename() == b_filename
        assert loaded_product.get_KSB_filename() == k_filename
        assert loaded_product.get_LensMC_filename() == l_filename
        assert loaded_product.get_MomentsML_filename() == m_filename
        assert loaded_product.get_REGAUSS_filename() == r_filename

        pass
    