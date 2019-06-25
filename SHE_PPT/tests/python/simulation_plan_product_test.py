""" @file simulation_plan_product_test.py

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

__updated__ = "2019-06-25"

from SHE_PPT.file_io import (read_xml_product, write_xml_product,
                             read_pickled_product, write_pickled_product)
from SHE_PPT.products import simulation_plan as prod


class TestSimulationPlanProduct(object):
    """A collection of tests for the shear estimates data product.

    """

    def test_validation(self):

        # Create the product
        product = prod.create_dpd_she_simulation_plan()

        # Check that it validates the schema
        product.validateBinding()

        pass

    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_simulation_plan()

        # Change the fits filenames
        subfilename = "test_file.fits"
        product.set_filename(subfilename)

        # Save the product in an XML file
        filename = "she_simulation_plan.xml"
        write_xml_product(product, filename, workdir=str(tmpdir))

        # Read back the XML file
        loaded_product = read_xml_product(filename)

        # Check that the filenames match
        assert loaded_product.get_filename() == subfilename

        pass

    def test_pickle_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_she_simulation_plan()

        # Change the fits filenames
        subfilename = "test_file.fits"
        product.set_filename(subfilename)

        # Save the product in an XML file
        filename = tmpdir.join("she_simulation_plan.xml")
        write_pickled_product(product, filename)

        # Read back the XML file
        loaded_product = read_pickled_product(filename)

        # Check that the filenames match
        assert loaded_product.get_filename() == subfilename

        pass
