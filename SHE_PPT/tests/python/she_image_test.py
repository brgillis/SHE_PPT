"""
File: tests/python/she_image_test.py

Created on: 08/18/17
"""

__updated__ = "2021-08-16"

#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# """This script gives a small demo of the image object.

import logging
import os
from copy import deepcopy

import galsim
import numpy as np
import pytest
from astropy.wcs import WCS

import SHE_PPT.she_image
from ElementsServices.DataSync import DataSync
from SHE_PPT import file_io, mdb
from SHE_PPT.constants.misc import SEGMAP_UNASSIGNED_VALUE
from SHE_PPT.constants.test_data import (MDB_PRODUCT_FILENAME, SYNC_CONF, TEST_DATA_LOCATION, TEST_FILES_MDB)

logging.basicConfig(level = logging.DEBUG)


class TestSheImage():

    @classmethod
    def setup_class(cls):

        sync = DataSync(SYNC_CONF, TEST_FILES_MDB)
        sync.download()
        mdb_filename = sync.absolutePath(os.path.join(TEST_DATA_LOCATION, MDB_PRODUCT_FILENAME))

        mdb.init(mdb_filename)

        cls.gain = mdb.get_gain(suppress_warnings = True)
        cls.read_noise = mdb.get_read_noise(suppress_warnings = True)

        # A filename for testing the file-saving:
        cls.testfilepath = "test_SHEImage.fits"  # Will be deleted by teardown_class()
        # For some tests we need several files:
        cls.testfilepaths = ["test_SHEImage_0.fits", "test_SHEImage_1.fits", "test_SHEImage_2.fits",
                             "test_SHEImage_3.fits"]

        # A WCS to use (from the auxdir)
        header_file = file_io.find_file("AUX/SHE_PPT/tpv_header.bin")
        header = file_io.read_pickled_product(header_file)
        cls.wcs = WCS(header)

        # A SHEImage object to play with
        cls.w = 50
        cls.h = 20
        array = np.random.randn(cls.w * cls.h).reshape((cls.w, cls.h))
        cls.img = SHE_PPT.she_image.SHEImage(array, header = header, wcs = cls.wcs)

    @classmethod
    def teardown_class(cls):

        # Delete all potentially created files:
        for testfilepath in cls.testfilepaths + [cls.testfilepath]:
            if os.path.exists(testfilepath):
                os.remove(testfilepath)

    def test_init(self):
        """Test that the object created by setup_class is as expected"""

        assert self.img.shape == (self.w, self.h)
        assert self.img.data.shape == self.img.shape

        assert self.img.mask.shape == self.img.shape
        assert self.img.noisemap is None
        assert self.img.segmentation_map is None
        assert self.img.background_map is None
        assert self.img.weight_map is None

    def test_mask(self):
        """Tests some mask functionality"""

        img = deepcopy(self.img)

        # Add a default mask and check its data type and values
        img.add_default_mask(force = True)
        assert img.mask.dtype == np.int32
        assert img.mask[5, 5] == 0
        assert img.boolmask[5, 5] == False
        assert img.mask.shape == (self.w, self.h)

        # Check that boolmask works if we change the mask
        img.mask[5, 5] = 100
        assert img.boolmask[5, 5] == True

        # Check that non-forcibly adding a default mask doesn't affect the existing mask
        img.add_default_mask(force = False)
        assert img.boolmask[5, 5] == True

        # Check that forcibly adding a default mask does affect the existing mask
        img.add_default_mask(force = True)
        assert img.boolmask[5, 5] == False

    def test_noisemap(self):
        """Test that the noisemap behaves appropriately."""

        img = deepcopy(self.img)

        # Add a default noisemap and check its data type and values
        img.add_default_noisemap(force = True)
        assert img.noisemap.dtype == float
        assert np.allclose(img.noisemap,
                           self.read_noise / self.gain * np.ones_like(img.data, dtype = img.noisemap.dtype))
        assert img.noisemap.shape == (self.w, self.h)

        # Check that non-forcibly adding a default noisemap doesn't affect the existing noisemap
        img.noisemap[5, 5] = 1.
        img.add_default_noisemap(force = False)
        assert np.isclose(img.noisemap[5, 5], 1.)

        # Check that forcibly adding a default noisemap does affect the existing noisemap
        img.add_default_noisemap(force = True)
        assert np.isclose(img.noisemap[5, 5], self.read_noise / self.gain)

        # Check that the noisemap is calculated correctly when a background map is present
        img.background_map = 1000 * np.ones_like(img.data, dtype = float)
        img.add_default_noisemap(force = True)
        assert np.allclose(img.noisemap, (self.read_noise / self.gain) + np.sqrt(1000 / self.gain) *
                           np.ones_like(img.data, dtype = img.noisemap.dtype))

    def test_segmentation_map(self):
        """Test that the segmentation map behaves appropriately."""

        img = deepcopy(self.img)

        # Add a default segmentation_map and check its data type and values
        img.add_default_segmentation_map(force = True)
        assert img.segmentation_map.dtype == np.int32
        assert np.allclose(img.segmentation_map,
                           SEGMAP_UNASSIGNED_VALUE * np.ones_like(img.data, dtype = img.segmentation_map.dtype))
        assert img.segmentation_map.shape == (self.w, self.h)

        # Check that non-forcibly adding a default segmentation_map doesn't affect the existing segmentation_map
        img.segmentation_map[5, 5] = 100
        img.add_default_segmentation_map(force = False)
        assert img.segmentation_map[5, 5] == 100

        # Check that forcibly adding a default segmentation_map does affect the existing segmentation_map
        img.add_default_segmentation_map(force = True)
        assert img.segmentation_map[5, 5] == 0

    def test_weight_map(self):
        """Test that the weight_map behaves appropriately."""

        img = deepcopy(self.img)

        # Add a default weight_map and check its data type and values
        img.add_default_weight_map(force = True)
        assert img.weight_map.dtype == float
        assert np.allclose(img.weight_map, np.ones_like(img.data, dtype = img.weight_map.dtype))
        assert img.weight_map.shape == (self.w, self.h)

        # Check that non-forcibly adding a default weight_map doesn't affect the existing weight_map
        img.weight_map[5, 5] = 0.
        img.add_default_weight_map(force = False)
        assert np.isclose(img.weight_map[5, 5], 0.)

        # Check that forcibly adding a default weight_map does affect the existing weight_map
        img.add_default_weight_map(force = True)
        assert np.isclose(img.weight_map[5, 5], 1.)

    def test_header(self):
        """Test the header behaves as expected."""

        img = deepcopy(self.img)

        img.add_default_header(force = True)

        img.header["temp1"] = (22.3, "Outside temp in degrees Celsius")
        img.header["INSTR"] = ("DMK21")
        img.header.set("tel", "14-inch Martini Dobson")

        assert img.header["TEMP1"] > 20.0  # capitalization does not matter
        assert len(img.header["INSTR"]) == 5

        # Check that non-forcibly adding a default header doesn't affect the existing header
        img.add_default_header(force = False)
        assert "INSTR" in img.header

        # Check that forcibly adding a default header does affect the existing header
        img.add_default_header(force = True)
        assert "INSTR" not in img.header

    def test_wcs_default(self):
        """Test the default wcs behaves as expected."""

        img = deepcopy(self.img)

        img.add_default_wcs(force = True)

        assert np.allclose(img.wcs.wcs.cdelt, np.array([1., 1.]))
        assert np.allclose(img.wcs.wcs.crval, np.array([0., 0.]))

        # Check that non-forcibly adding a default wcs doesn't affect the existing wcs
        img.wcs.wcs.cdelt[0] = 2.
        img.add_default_wcs(force = False)
        assert np.isclose(img.wcs.wcs.cdelt[0], 2.)

        # Check that forcibly adding a default wcs does affect the existing wcs
        img.add_default_wcs(force = True)
        assert np.isclose(img.wcs.wcs.cdelt[0], 1.)

    def test_fits_read_write(self):
        """We save the small SHEImage, read it again, and compare both versions"""

        img = deepcopy(self.img)

        # To have a non-trivial image, we tweak it a bit:
        img.noisemap = 1.0 + 0.01 * np.random.randn(self.w * self.h).reshape((self.w, self.h))
        img.add_default_mask()
        img.mask[0:10, :] = 1
        img.mask[10:20, :] = 255
        img.mask[30:40, :] = -10456.34  # will get converted and should not prevent the test from working
        img.add_default_segmentation_map()
        img.segmentation_map[10:20, 20:30] = 1

        img.wcs = self.wcs

        img.write_to_fits(self.testfilepath, overwrite = False)

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepath)

        assert np.allclose(img.data, rimg.data)
        assert np.allclose(img.mask, rimg.mask)
        assert np.allclose(img.noisemap, rimg.noisemap)
        assert np.allclose(img.segmentation_map, rimg.segmentation_map)

        # Check the wcs behaves the same
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            # Note - not testing here that we recover proper ra/dec or x/y, since that's covered in separate test
            # Just testing WCS from writing/reading is the same here

            ra1, dec1 = img.pix2world(x, y, origin = 1)
            ra2, dec2 = rimg.pix2world(x, y, origin = 1)

            assert np.allclose((ra1, dec1), (ra2, dec2))

            x1, y1 = img.world2pix(ra, dec, origin = 1)
            x2, y2 = rimg.world2pix(ra, dec, origin = 1)

            assert np.allclose((x1, y1), (x2, y2))

        # Also check the transformation matrices match up
        assert np.allclose(img.get_world2pix_transformation(0, 0),
                           rimg.get_world2pix_transformation(0, 0))
        assert np.allclose(img.get_pix2world_transformation(0, 0),
                           rimg.get_pix2world_transformation(0, 0))

        # We test that the header did not get changed # FIXME disabled for now
        # assert len(list(rimg.header.keys())) == 3
        # assert str(repr(img.header)) == str(repr(rimg.header))

    def test_read_from_fits_files(self):
        """At least a small test of reading from individual FITS files"""

        img = SHE_PPT.she_image.SHEImage(np.random.randn(100).reshape(10, 10) + 200.0)
        img.mask = np.ones_like(img.data, dtype = np.int32)
        img.noisemap = 1.0 + 0.01 * np.random.randn(100).reshape(10, 10)
        img.write_to_fits(self.testfilepaths[0])

        img.mask[:, :] = 2
        img.write_to_fits(self.testfilepaths[1])

        img.noisemap = 1000.0 + 0.01 * np.random.randn(100).reshape(10, 10)
        img.write_to_fits(self.testfilepaths[2])

        img.segmentation_map = 4 * np.ones_like(img.data, dtype = np.int32)
        img.write_to_fits(self.testfilepaths[3])

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepaths[0])
        assert rimg.mask[0, 0] == 1

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepaths[0],
                                                         mask_filepath = self.testfilepaths[1],
                                                         noisemap_filepath = self.testfilepaths[2],
                                                         segmentation_map_filepath = self.testfilepaths[3])
        assert rimg.noisemap[0, 0] > 500.0
        assert rimg.segmentation_map[0, 0] == 4

        with pytest.raises(ValueError):  # As the primary HDU of mask_filepath is not a np.uint8, this will fail:
            _ = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepaths[0],
                                                          mask_filepath = self.testfilepaths[1],
                                                          noisemap_filepath = self.testfilepaths[2],
                                                          segmentation_map_filepath = self.testfilepaths[3],
                                                          mask_ext = None)

    def test_extracted_stamp_is_view(self):
        """Checks that the extracted stamp is a view, not a copy"""

        stamp = self.img.extract_stamp(10.5, 10.5, 3)  # central pixel of stamp is index [10, 10] of the big array
        stamp.data[1, 1] = -50.0  # the central pixel, modifed both here and in img

        assert self.img.data[10, 10] == stamp.data[1, 1]

    def test_extract_stamp_not_square(self):
        """Testing that non-square stamps are correctly extracted"""

        stamp = self.img.extract_stamp(10.0, 10.0, 5)
        assert stamp.shape == (5, 5)
        stamp = self.img.extract_stamp(10.0, 10.0, 4, 6)
        assert stamp.shape == (4, 6)

    def test_extract_stamp_indexconvs(self):
        """Test the effect of different indexconvs"""

        bottomleftpixel_numpy = self.img.extract_stamp(0.5, 0.5, 1)
        bottomleftpixel_sex = self.img.extract_stamp(1.0, 1.0, 1, indexconv = "sextractor")
        assert bottomleftpixel_numpy.data == bottomleftpixel_sex.data

    def test_extract_stamp(self):
        """We test that the stamp extraction get the correct data"""

        size = 64
        array = np.random.randn(size ** 2).reshape((size, size))
        array[0:32, 0:32] = 1.0e15  # bottom-left stamp is high and constant

        img = SHE_PPT.she_image.SHEImage(array)

        img.add_default_mask()
        img.mask[32:64, :] = True

        img.noisemap = 1000.0 + np.random.randn(size ** 2).reshape((size, size))

        img.add_default_segmentation_map()
        img.segmentation_map[0:32, :] = 1
        img.segmentation_map[32:64, :] = 2

        img.add_default_header()
        img.header["foo"] = "bar"

        # Testing extracted shape and extracted mask
        eimg = img.extract_stamp(16.4, 15.6, 32)
        assert eimg.shape == (32, 32)
        assert np.sum(eimg.mask) == 0  # Nothing should be masked
        assert np.sum(eimg.segmentation_map) == 1 * np.product(eimg.shape)  # Should all belong to object 1
        assert np.std(eimg.data) < 1.0e-10
        assert np.mean(eimg.noisemap) > 900.0 and np.mean(eimg.noisemap) < 1100.0

        eimg = img.extract_stamp(32 + 16.4, 32 + 15.6, 32)
        assert eimg.shape == (32, 32)
        assert np.sum(eimg.mask) == 1 * np.product(eimg.shape)  # This one is fully masked
        assert np.sum(eimg.segmentation_map) == 2 * np.product(eimg.shape)  # Should all belong to object 2
        assert np.std(eimg.data) > 1.0e-10

        # And the header:
        eimg = img.extract_stamp(5, 5, 5)
        assert eimg.header is None
        eimg = img.extract_stamp(5, 5, 5, keep_header = True)
        assert len(list(eimg.header.keys())) == 1  # The "foo"

        # Test setting or not setting default properties for an extracted stamp
        simple_img = SHE_PPT.she_image.SHEImage(array)

        simple_stamp = simple_img.extract_stamp(16.4, 15.6, 32)

        assert simple_stamp.mask.shape == simple_stamp.shape
        assert simple_stamp.noisemap is None
        assert simple_stamp.segmentation_map is None
        assert simple_stamp.background_map is None
        assert simple_stamp.weight_map is None
        assert simple_stamp.header is None
        assert simple_stamp.wcs is None

        default_stamp = simple_img.extract_stamp(16.4, 15.6, 32, force_all_properties = True)

        assert default_stamp.mask is not None
        assert default_stamp.noisemap is not None
        assert default_stamp.segmentation_map is not None
        assert default_stamp.background_map is not None
        assert default_stamp.weight_map is not None
        assert default_stamp.header is not None
        assert default_stamp.wcs is not None

    def test_extract_stamp_oob(self):
        """We test that the stamp extraction works as desired for stamps not entirely within the image"""

        array = np.array([[0, 1, 2, 3, 4], [10, 11, 12, 13, 14], [20, 21, 22, 23, 24], [30, 31, 32, 33, 34]])
        img = SHE_PPT.she_image.SHEImage(array)
        # This image looks like (values give xy coords...)
        # 04 14 24 34
        # 03 13 23 33
        # 02 12 22 32
        # 01 11 21 31
        # 00 10 20 30

        stamp = img.extract_stamp(0.5, 0.5, 3)
        # This is:
        # XX 01 11
        # XX 00 10
        # XX XX XX
        assert stamp.data[2, 2] == 11
        assert stamp.data[2, 1] == 10
        assert stamp.data[0, 0] == 0
        assert stamp.boolmask[1, 1] == False
        assert stamp.boolmask[0, 0] == True

        img.add_default_mask()
        img.add_default_noisemap()
        img.add_default_segmentation_map()
        stamp = img.extract_stamp(-10.0, 20.0, 3)
        # This one is completely out of bounds:
        assert np.alltrue(stamp.boolmask)
        assert np.allclose(stamp.noisemap, 0.0)
        assert np.allclose(stamp.segmentation_map, SEGMAP_UNASSIGNED_VALUE)

        stamp = img.extract_stamp(3.5, 1.5, 3, 1)
        # This is
        # 21 31 XX
        assert stamp.data[0, 0] == 21
        assert stamp.data[1, 0] == 31
        assert stamp.boolmask[2, 0] == True

    def test_offset(self):
        """Testing the offset property"""

        size = 64
        array = np.random.randn(size ** 2).reshape((size, size))
        img = SHE_PPT.she_image.SHEImage(array)

        # Testing expected behavior of stamp extraction
        stamp = img.extract_stamp(2.5, 3.5, 1)
        assert stamp.offset[0] == 2
        assert stamp.offset[1] == 3

        # Does it survive FITS io?
        stamp.write_to_fits(self.testfilepath, overwrite = True)
        rstamp = SHE_PPT.she_image.SHEImage.read_from_fits(self.testfilepath)
        assert rstamp.offset[0] == 2
        assert rstamp.offset[1] == 3

    def test_get_object_mask(self):
        """Test that the get_object_mask function behaves as expected."""

        import SHE_PPT.mask as m

        # Create an object for testing
        mask = np.array(((0, m.masked_near_edge, m.masked_off_image),
                         (0, m.masked_near_edge, m.masked_off_image),
                         (m.masked_bad_pixel, m.masked_near_edge, m.masked_off_image)),
                        dtype = np.int32)

        segmap = np.array(((1, 1, 1),
                           (SEGMAP_UNASSIGNED_VALUE, SEGMAP_UNASSIGNED_VALUE, SEGMAP_UNASSIGNED_VALUE),
                           (2, 2, 2)),
                          dtype = np.int32)
        img = SHE_PPT.she_image.SHEImage(data = np.zeros_like(mask),
                                         mask = mask,
                                         segmentation_map = segmap)

        # Test for various possible cases

        # Don't mask suspect or unassigned
        desired_bool_mask = np.array(((False, False, True),
                                      (False, False, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert (img.get_object_mask(1, mask_suspect = False, mask_unassigned = False)
                == desired_bool_mask).all()

        # Mask suspect, not unassigned
        desired_bool_mask = np.array(((False, True, True),
                                      (False, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert (img.get_object_mask(1, mask_suspect = True, mask_unassigned = False)
                == desired_bool_mask).all()

        # Mask unassigned, not suspect
        desired_bool_mask = np.array(((False, False, True),
                                      (True, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert (img.get_object_mask(1, mask_suspect = False, mask_unassigned = True)
                == desired_bool_mask).all()

        # Mask suspect and unassigned
        desired_bool_mask = np.array(((False, True, True),
                                      (True, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert (img.get_object_mask(1, mask_suspect = True, mask_unassigned = True)
                == desired_bool_mask).all()

    def test_pix2world(self):
        """Test that pix2world works properly"""

        # Test with values coming from calculation assuming origin=1
        for x, y, ex_ra, ex_dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                                    (24, 38, 52.53677316085, -28.75899827058671),
                                    (1012, 4111, 52.876229370322626, -28.686527560717373)):

            ra0, dec0 = self.img.pix2world(x + 1, y + 1, origin = 0)
            assert np.allclose((ra0, dec0), (ex_ra, ex_dec))

            ra1, dec1 = self.img.pix2world(x, y, origin = 1)
            assert np.allclose((ra1, dec1), (ex_ra, ex_dec))

    def test_world2pix(self):
        """Test that world2pix works properly"""

        # Test with values coming from calculation assuming origin=1
        for ex_x, ex_y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                                    (24, 38, 52.53677316085, -28.75899827058671),
                                    (1012, 4111, 52.876229370322626, -28.686527560717373)):

            x0, y0 = self.img.world2pix(ra, dec, origin = 0)
            assert np.allclose((x0 + 1, y0 + 1), (ex_x, ex_y))

            x1, y1 = self.img.world2pix(ra, dec, origin = 1)
            assert np.allclose((x1, y1), (ex_x, ex_y))

    def test_transformations(self):

        # Check that the transformations are approximately the inverses of each other

        for spatial_ra in (False, True):
            for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                                  (24, 38, 52.53677316085, -28.75899827058671),
                                  (1012, 4111, 52.876229370322626, -28.686527560717373)):

                pix2world_transformation = self.img.get_pix2world_transformation(x, y, spatial_ra = spatial_ra,
                                                                                 origin = 1)
                world2pix_transformation = self.img.get_world2pix_transformation(
                    ra, dec, spatial_ra = spatial_ra, origin = 1)

                double_transformation = pix2world_transformation @ world2pix_transformation

                assert np.allclose(double_transformation, np.array([[1., 0.], [0., 1.]]),
                                   rtol = 1e-2, atol = 1e-3)

                # Check for the normalized transformations as well
                normed_pix2world_transformation = self.img.get_pix2world_transformation(x, y, spatial_ra = spatial_ra,
                                                                                        origin = 1,
                                                                                        norm = True)
                normed_world2pix_transformation = self.img.get_world2pix_transformation(
                    ra, dec, spatial_ra = spatial_ra, origin = 1, norm = True)

                normed_double_transformation = pix2world_transformation @ world2pix_transformation

                assert np.allclose(normed_double_transformation, np.array([[1., 0.], [0., 1.]]),
                                   rtol = 1e-2, atol = 1e-3)

                # These should also all have a determinant of 1 or -1

                assert np.isclose(np.abs(np.linalg.det(normed_pix2world_transformation)), 1.)
                assert np.isclose(np.abs(np.linalg.det(normed_world2pix_transformation)), 1.)

                if spatial_ra:
                    continue
                # Check that these can be applied successfully

                dx = 2.0
                dy = 0.5

                new_radec = np.array([[ra], [dec]]) + pix2world_transformation @ np.array([[dx], [dy]])
                new_ra = new_radec[0, 0]
                new_dec = new_radec[1, 0]

                assert np.allclose((new_ra, new_dec), self.img.pix2world(x + dx, y + dy),
                                   rtol = 1e-5, atol = 1e-4)

                dra = 2.0 / 3600
                ddec = 0.5 / 3600

                new_xy = np.array([[x], [y]]) + world2pix_transformation @ np.array([[dra], [ddec]])
                new_x = new_xy[0, 0]
                new_y = new_xy[1, 0]

                assert np.allclose((new_x, new_y), self.img.world2pix(ra + dra, dec + ddec, origin = 1),
                                   rtol = 1e-2, atol = 1e-4)

    def test_rotation(self):

        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            # Get pix2world angles for each of a few different test steps
            pix2world_angles = []
            world2pix_angles = []
            for dx, dy in ((0.1, 0.0),
                           (0.1, 0.1),
                           (0.0, 0.1),
                           (-0.1, 0.1),
                           (-0.1, 0.0),
                           (-0.1, -0.1),
                           (0.0, -0.1),
                           (0.1, -0.1)):
                pix2world_angle = self.img.estimate_pix2world_rotation_angle(x, y, dx = dx, dy = dy, origin = 1)
                if pix2world_angle < 0:
                    pix2world_angle += 2 * np.pi
                elif pix2world_angle > 2 * np.pi:
                    pix2world_angle -= 2 * np.pi

                world2pix_angle = self.img.estimate_world2pix_rotation_angle(ra, dec,
                                                                             dra = dx / 3600,
                                                                             ddec = dy / 3600,
                                                                             origin = 1)
                if world2pix_angle < 0:
                    world2pix_angle += 2 * np.pi
                elif world2pix_angle > 2 * np.pi:
                    world2pix_angle -= 2 * np.pi

                pix2world_angles.append(pix2world_angle)
                world2pix_angles.append(world2pix_angle)

            # Get the mean for each, and check they're approximately opposites
            pix2world_angle = np.mean(pix2world_angles)
            world2pix_angle = np.mean(world2pix_angles)

            assert np.isclose(pix2world_angle, world2pix_angle + np.pi, rtol = 0.05)

            # Now, create rotation matrices for both, and check these match what we get
            # from the SVD method
            pix2world_rotation_matrix_1 = np.array([[np.cos(pix2world_angle), -np.sin(pix2world_angle)],
                                                    [np.sin(pix2world_angle), np.cos(pix2world_angle)]])
            world2pix_rotation_matrix_1 = np.array([[np.cos(world2pix_angle), -np.sin(world2pix_angle)],
                                                    [np.sin(world2pix_angle), np.cos(world2pix_angle)]])

            pix2world_rotation_matrix_2 = self.img.get_pix2world_rotation(x, y, origin = 1)
            world2pix_rotation_matrix_2 = self.img.get_world2pix_rotation(ra, dec, origin = 1)

            assert np.allclose(pix2world_rotation_matrix_1, pix2world_rotation_matrix_2, rtol = 0.02, atol = 0.002)
            assert np.allclose(world2pix_rotation_matrix_1, world2pix_rotation_matrix_2, rtol = 0.02, atol = 0.002)

            return

    def test_galsim_wcs(self):
        """Test that we can generate and use a GalSim-style WCS."""

        # Make a copy of the image so we can modify it safely
        img = deepcopy(self.img)

        # Test getting the WCS from the header
        img.wcs = None

        # Test with values coming from calculation assuming origin=1
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            xy_pos = img.galsim_wcs.toImage(galsim.CelestialCoord(ra * galsim.degrees, dec * galsim.degrees))
            assert np.allclose((xy_pos.x, xy_pos.y), (x, y))
            radec_pos = img.galsim_wcs.toWorld(galsim.PositionD(x, y))
            # Need to divide out units for numpy to understand the values
            assert np.allclose((radec_pos.ra / galsim.degrees, radec_pos.dec / galsim.degrees), (ra, dec))

        # Make another copy of the image so we can start fresh
        img = deepcopy(self.img)

        # Test getting the WCS from the astropy WCS
        img.header = None

        # Test with values coming from calculation assuming origin=1
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            xy_pos = img.galsim_wcs.toImage(galsim.CelestialCoord(ra * galsim.degrees, dec * galsim.degrees))
            assert np.allclose((xy_pos.x, xy_pos.y), (x, y))
            radec_pos = img.galsim_wcs.toWorld(galsim.PositionD(x, y))
            # Need to divide out units for numpy to understand the values
            assert np.allclose((radec_pos.ra / galsim.degrees, radec_pos.dec / galsim.degrees), (ra, dec))

        # Test with an OffsetWCS as well

        # Make another copy of the image so we can start fresh
        img = deepcopy(self.img)

        test_scale = 0.1
        test_x_offset = 100
        test_y_offset = 200
        test_x_im = 15
        test_y_im = 45

        test_x_world = test_x_offset + test_scale * test_x_im
        test_y_world = test_y_offset + test_scale * test_y_im

        img.galsim_wcs = galsim.wcs.OffsetWCS(scale = test_scale,
                                              origin = galsim.PositionD(0., 0.),
                                              world_origin = galsim.PositionD(test_x_offset, test_y_offset))

        im_pos = galsim.PositionD(test_x_im, test_y_im)
        world_pos = galsim.PositionD(test_x_world, test_y_world)

        test_world_pos = img.galsim_wcs.toWorld(im_pos)
        test_im_pos = img.galsim_wcs.toImage(world_pos)

        assert np.allclose((im_pos.x, im_pos.y), (test_im_pos.x, test_im_pos.y))
        assert np.allclose((world_pos.x, world_pos.y), (test_world_pos.x, test_world_pos.y))

    def test_decomposition(self):
        """Test that we can get the expected local decomposition of a WCS."""

        # Test with values coming from calculation assuming origin=1
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            world2pix_decomposition = self.img.get_world2pix_decomposition(ra, dec)
            pix2world_decomposition = self.img.get_pix2world_decomposition(x, y)

            # Check the scales are inverses
            assert np.isclose(world2pix_decomposition[0], 1. / pix2world_decomposition[0])

            # Shear is checked for the non-celestial WCS

            # Check the angles are opposite (need to divide out units for numpy to understand the values)
            assert np.isclose(world2pix_decomposition[2] / galsim.degrees, -
            pix2world_decomposition[2] / galsim.degrees)

            # Check the flip is the same
            assert world2pix_decomposition[3] == pix2world_decomposition[3]

            # Check the angle matches what we get in the rotation matrix
            pix2world_rotation_matrix = self.img.get_pix2world_rotation(x, y, origin = 1)
            assert np.isclose(pix2world_decomposition[2].cos(), pix2world_rotation_matrix[0, 0], rtol = 1e-4)
            assert np.isclose(pix2world_decomposition[2].sin(), pix2world_rotation_matrix[0, 1], rtol = 1e-4)

        # Test with a simple Shear WCS

        # Make a copy of the image so we can modify it safely
        img = deepcopy(self.img)

        w2p_g1 = 0.1
        w2p_g2 = 0.2
        p2w_scale = 0.01

        w2p_shear = galsim.Shear(g1 = w2p_g1, g2 = w2p_g2)

        img.galsim_wcs = galsim.wcs.ShearWCS(scale = p2w_scale, shear = w2p_shear)

        test_w2p_scale, test_w2p_shear, _, _ = img.get_world2pix_decomposition(0, 0)
        test_p2w_scale, test_p2w_shear, _, _ = img.get_pix2world_decomposition(0, 0)

        assert np.isclose(test_w2p_scale, 1. / p2w_scale)
        assert np.allclose((w2p_shear.g1, w2p_shear.g2), (test_w2p_shear.g1, test_w2p_shear.g2))

        assert np.isclose(test_p2w_scale, p2w_scale)
        assert np.allclose((-w2p_shear.g1, -w2p_shear.g2), (test_p2w_shear.g1, test_p2w_shear.g2))

    def test_equality(self):

        # Test we get equal when we expect it
        img_copy = deepcopy(self.img)
        assert self.img == img_copy

        # Test we get inequal when we change the copy
        img_copy.data += 1
        assert self.img != img_copy
