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

__updated__ = "2021-08-13"

import numpy as np
import pytest
from astropy.io import fits

from SHE_PPT import detector as dtc
from SHE_PPT.constants.fits import SEGMENTATION_TAG
from SHE_PPT.file_io import (SheFileReadError, read_xml_product, write_xml_product)
from SHE_PPT.products import mer_segmentation_map as prod
from SHE_PPT.testing.utility import SheTestCase


class TestMosaicProduct(SheTestCase):
    """A collection of tests for the mosaic data product.

    """

    def test_validation(self):
        # Create the product
        product = prod.create_dpd_mer_mosaic(data_filename="junk", )

        # Check that it validates the schema
        product.validateBinding()

    def test_xml_writing_and_reading(self, tmpdir):
        # Create the product
        product = prod.create_dpd_mer_mosaic(data_filename="junk", )

        # Change the fits file names
        data_filename = "test_file_data.fits"
        product.set_data_filename(data_filename)

        # Save the product in an xml file
        write_xml_product(product, "mer_mosaic.xml", workdir=str(tmpdir))

        # Read back the xml file
        loaded_product = read_xml_product("mer_mosaic.xml", workdir=str(tmpdir))

        # Check that it's the same
        assert loaded_product.get_data_filename() == "data/" + data_filename

        return

    def test_load_mosaic_hdu(self, tmpdir):
        # Create and save the product with a junk filename first
        product = prod.create_dpd_mer_mosaic(data_filename="junk", )

        filename = str(tmpdir.join("mer_mosaic.bin"))
        write_xml_product(product, filename)

        # Check that it raises exceptions when expected

        with pytest.raises(SheFileReadError):
            _ = prod.load_mosaic_hdu(filename="bad_filename.junk")
        with pytest.raises(IOError):
            _ = prod.load_mosaic_hdu(filename=filename)

        # Now save it pointing to an existing fits file and check that it works

        test_array = np.zeros((10, 20))
        test_array[0, 0] = 1
        detector_x = 2
        detector_y = 3

        phdu = fits.PrimaryHDU(data=test_array,
                               header=fits.header.Header((("EXTNAME", dtc.get_id_string(detector_x, detector_y)
                                                           + "." + SEGMENTATION_TAG),)))

        data_filename = str(tmpdir.join("mosaic_data.fits"))
        phdu.writeto(data_filename, overwrite=True)

        product.set_data_filename(data_filename)
        write_xml_product(product, filename)

        loaded_hdu = prod.load_mosaic_hdu(filename=filename,
                                          detector_x=detector_x,
                                          detector_y=detector_y)

        assert (loaded_hdu.data == test_array).all()

        # Now test with a multi-HDU data image

        test_array2 = np.zeros((20, 40))
        test_array2[0, 0] = 2
        detector_x2 = 4
        detector_y2 = 5

        hdu2 = fits.ImageHDU(data=test_array2,
                             header=fits.header.Header((("EXTNAME", dtc.get_id_string(detector_x2, detector_y2)
                                                         + "." + SEGMENTATION_TAG),)))

        hdulist = fits.HDUList([phdu, hdu2])
        hdulist.writeto(data_filename, overwrite=True)

        loaded_hdu1 = prod.load_mosaic_hdu(filename=filename,
                                           hdu=0)

        assert (loaded_hdu1.data == test_array).all()

        loaded_hdu2 = prod.load_mosaic_hdu(filename=filename,
                                           hdu=1)

        assert (loaded_hdu2.data == test_array2).all()

        loaded_hdu1 = prod.load_mosaic_hdu(filename=filename,
                                           detector_x=detector_x,
                                           detector_y=detector_y)

        assert (loaded_hdu1.data == test_array).all()

        loaded_hdu2 = prod.load_mosaic_hdu(filename=filename,
                                           detector_x=detector_x2,
                                           detector_y=detector_y2)

        assert (loaded_hdu2.data == test_array2).all()

        return
