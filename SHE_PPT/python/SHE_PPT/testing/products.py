""" @file testing/products.py

    Created 16 Aug 2021

    Functions related to the testing of tables and table formats
"""

__updated__ = "2021-08-16"

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import abc
import os
from typing import Any, Optional

from SHE_PPT.file_io import DATA_SUBDIR, read_xml_product, write_xml_product
from SHE_PPT.testing.utility import SheTestCase
from SHE_PPT.utility import is_any_type_of_none


class ProductTester(SheTestCase, abc.ABC):
    """A collection of tests for the shear estimates data product.
    """

    product_class: Any
    product_type_name: Optional[Any] = None
    _empty_product: Optional[Any] = None

    @property
    def empty_product(self):
        if self._empty_product is None:
            self._empty_product = self.product_class()
        return self._empty_product

    def init_product(self, *args, **kwargs):

        if hasattr(self.empty_product, "init_product"):
            return self.empty_product.init_product(*args, **kwargs)
        elif hasattr(self.empty_product, "d_init_functions") and self.product_type_name:
            return self.empty_product.d_init_functions[self.product_type_name](*args, **kwargs)
        else:
            raise ValueError(f"Product class {self.product_class} of type {self.product_type_name} has no "
                             f"recognized function to initialize a product.")

    def test_validation(self):

        # Create the product
        p = self.init_product()

        # Check that it validates the schema
        p.validateBinding()

    def test_default_filenames(self):
        """Test that all filenames in a default product are empty.
        """

        p = self.init_product()

        for filename in p.get_all_filenames():
            assert is_any_type_of_none(filename)


class SimpleDataProductTester(ProductTester, abc.ABC):

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        p = self.init_product()

        # Change the fits filenames
        subfilename = "test_file.fits"
        p.set_filename(subfilename)

        # Determine a file to write the product to
        filename = f"{p.Header.ProductType}.xml"
        qualified_filename = os.path.join(str(tmpdir), filename)

        # If the file already exists (perhaps from a previous test), delete it
        if os.path.exists(qualified_filename):
            os.remove(qualified_filename)

        # Save the product in an XML file
        write_xml_product(p, filename, workdir = str(tmpdir))

        # Check that the file exists
        assert os.path.exists(qualified_filename)

        # Read back the XML file
        loaded_p = read_xml_product(filename, workdir = str(tmpdir))

        # Check that the filenames match
        assert loaded_p.get_data_filename() == f"data/{subfilename}"

        # Delete the file now
        os.remove(qualified_filename)


class MethodsProductTester(ProductTester, abc.ABC):

    def test_xml_writing_and_reading(self, tmpdir):
        # Create the product
        p = self.init_product()

        # Change the fits filenames
        k_filename = "test_file_k.fits"
        p.set_KSB_filename(k_filename)
        l_filename = "test_file_l.fits"
        p.set_LensMC_filename(l_filename)
        m_filename = "test_file_m.fits"
        p.set_MomentsML_filename(m_filename)
        r_filename = "test_file_r.fits"
        p.set_REGAUSS_filename(r_filename)

        # Save the product in an XML file
        write_xml_product(p, "she_she_measurements.xml", workdir = str(tmpdir))

        # Read back the XML file
        loaded_p = read_xml_product("she_she_measurements.xml", workdir = str(tmpdir))

        # Check that the filenames coincide
        assert loaded_p.get_KSB_filename() == DATA_SUBDIR + k_filename
        assert loaded_p.get_LensMC_filename() == DATA_SUBDIR + l_filename
        assert loaded_p.get_MomentsML_filename() == DATA_SUBDIR + m_filename
        assert loaded_p.get_REGAUSS_filename() == DATA_SUBDIR + r_filename
