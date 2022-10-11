""" @file detections_product_test.py

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

import pytest
from SHE_PPT.file_io import read_xml_product, write_xml_product
from SHE_PPT.products import phz_pf_output_catalog as prod


class TestPhotozProduct(object):
    """A collection of tests for the shear estimates data product.

    """
    @pytest.mark.skip(reason="Skip for now")
    def test_validation(self):

        # Create the product
        product = prod.create_dpd_photoz_catalog(
            "photoz_catalog.fits",
            "class_catalog.fits",
            "gal_sed_catalog.fits",
            "star_sed_catalog.fits",
            "phys_param_catalog.fits")

        # Check that it validates the schema
        product.validateBinding()

        return

    # @pytest.mark.skip(reason="Skip for now")
    def test_xml_writing_and_reading(self, tmpdir):

        # Create the product
        product = prod.create_dpd_photoz_catalog(
            "photoz_catalog.fits",
            "class_catalog.fits",
            "gal_sed_catalog.fits",
            "star_sed_catalog.fits",
            "phys_param_catalog.fits")

        # Change the fits filenames
        subfilename = "test_phz_file.fits"
        product.set_photoz_filename(subfilename)

        # Save the product in an XML file
        write_xml_product(product, "phz_photoz.xml", workdir=str(tmpdir))
        # Read back the XML file
        loaded_product = read_xml_product("phz_photoz.xml", workdir=str(tmpdir))

        # Check that the filenames match
        assert loaded_product.get_photoz_filename() == "data/" + subfilename
        print("DP: ",loaded_product.Header.ProductType)
        all_filenames = loaded_product.get_all_filenames()
        assert len(all_filenames)==5
        assert len([fname for fname in all_filenames if fname])==5
        return
