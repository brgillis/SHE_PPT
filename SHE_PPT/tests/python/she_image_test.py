""" @file she_image_test.py

    Created 18 Aug 2017

    Unit tests for the `SHE_PPT.she_image` module.
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

import logging
import os
from copy import deepcopy

import galsim
import numpy as np
import pytest
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from SHE_PPT import file_io, mdb
from SHE_PPT.constants.fits import CCDID_LABEL
from SHE_PPT.constants.misc import SEGMAP_UNASSIGNED_VALUE
from SHE_PPT.file_io import get_qualified_filename
from SHE_PPT.she_image import (DETECTOR_SHAPE, D_ATTR_CONVERSIONS, D_IMAGE_DTYPES, NOISEMAP_DTYPE, PRIMARY_TAG,
                               SEG_DTYPE, SHEImage,
                               WGT_DTYPE, )
from SHE_PPT.testing.utility import SheTestCase

logging.basicConfig(level = logging.DEBUG)


def estimate_pix2world_rotation_angle(image: SHEImage,
                                      x: float,
                                      y: float,
                                      dx: float = 0.01,
                                      dy: float = 0.01,
                                      origin = 0):
    """Estimates the local rotation angle between pixel and world (-ra/dec) coordinates at the specified location.
    This function is used to test the `get_pix2world_rotation` method of the `SHEImage` class for validity.

    Parameters
    ----------
    image : SHEImage
        The image object to use.
    x : float
        x pixel coordinate. Note: dx and dy are required here since, due to distortion in the transformation,
        we can't assume the rotation angle will be independent of them.
    y : float
        idem for y
    dx : float, default=0.01
        Differential x step to use in calculating transformation matrix
    dy : float, default=0.01
        idem for y
    origin : {0,1}
        Coordinate in the upper left corner of the image.
        In FITS and Fortran standards, this is 1.
        In Numpy and C standards this is 0.
        (from astropy.wcs)

    Raises
    ------
    AttributeError
        This object does not have a wcs set up
    ValueError
        dx and dy are 0, or dec is too close to pole

    Returns
    -------
    rotation_angle : float
        Rotation angle from pixel coords to world coords in radians

    """

    # Correct for offset if applicable
    if image.offset is not None:
        x = x + image.offset[0]
        y = y + image.offset[1]

    if (dx == 0) and (dy == 0):
        raise ValueError("Differentials dx and dy must not both be zero.")

    # We'll calculate the transformation empirically by using small steps
    # in x and y
    ra_0, dec_0 = image.pix2world(x, y, origin = origin)
    ra_1, dec_1 = image.pix2world(x + dx, y + dy, origin = origin)

    cos_dec = np.cos(dec_0 * np.pi / 180)

    if cos_dec <= 0.01:
        raise ValueError("Dec too close to pole for accurate calculation.")

    dra = -(ra_1 - ra_0)
    ddec = (dec_1 - dec_0)

    x_y_angle = np.arctan2(dx, dy)
    ra_dec_angle = np.arctan2(dra * cos_dec, ddec)

    rotation_angle = ra_dec_angle - x_y_angle

    return rotation_angle


def estimate_world2pix_rotation_angle(image: SHEImage,
                                      ra: float,
                                      dec: float,
                                      dra: float = 0.01 / 3600,
                                      ddec: float = 0.01 / 3600,
                                      origin: {0, 1} = 0) -> float:
    """Gets the local rotation angle between world (-ra/dec) and pixel coordinates at the specified location.
    This function is used to test the `get_world2pix_rotation` method of the `SHEImage` class for validity.

    Parameters
    ----------
    image : SHEImage
        The image object to use.
    ra : float
        Right Ascension (RA) world coordinate in degrees
    dec : float
        Declination (Dec) world coordinate in degrees
    dra : float, default=0.01/3600
        Differential ra step in degrees to use in calculating transformation matrix. Note: dra and ddec are
        required here since, due to distortion in the transformation, we can't assume the rotation angle will be
        independent of them.
    ddec : float, default=0.01/3600
        idem for dec
    origin : {0,1}
        Coordinate in the upper left corner of the image.
        In FITS and Fortran standards, this is 1.
        In Numpy and C standards this is 0.
        (from astropy.wcs)



    Raises
    ------
    AttributeError
        This object does not have a wcs set up
    ValueError
        dra and ddec are 0, or dec is too close to pole

    Returns
    -------
    rotation_angle : float
        Rotation angle from world coords to pixel coords in radians

    """

    if (dra == 0) and (ddec == 0):
        raise ValueError("Differentials dx and dy must not both be zero.")

    cos_dec = np.cos(dec * np.pi / 180)

    if cos_dec <= 0.01:
        raise ValueError("Dec too close to pole for accurate calculation.")

    # We'll calculate the transformation empirically by using small steps in x and y
    x_0, y_0 = image.world2pix(ra, dec, origin = origin)
    x_1, y_1 = image.world2pix(ra - dra, dec + ddec, origin = origin)

    dx = (x_1 - x_0)
    dy = (y_1 - y_0)

    x_y_angle = np.arctan2(dx, dy)
    ra_dec_angle = np.arctan2(dra * cos_dec, ddec)

    rotation_angle = x_y_angle - ra_dec_angle

    return rotation_angle


class TestSheImage(SheTestCase):
    """Unit tests for the SHEImage class.
    """

    # Class attributes

    # A filename for testing the file-saving
    TEST_FILENAME = "test_SHEImage.fits"
    # For some tests we need several files:
    L_TEST_FILENAMES = ["test_SHEImage_0.fits", "test_SHEImage_1.fits", "test_SHEImage_2.fits",
                        "test_SHEImage_3.fits"]

    def setup_workdir(self):
        """Set up a workdir for tests, with a downloaded MDB file.
        """

        self._download_mdb()

        self.gain = mdb.get_gain(suppress_warnings = True)
        self.read_noise = mdb.get_read_noise(suppress_warnings = True)

        # A WCS to use (from the auxdir)
        header_file = file_io.find_file("AUX/SHE_PPT/tpv_header.bin")
        header = file_io.read_pickled_product(header_file)
        self.wcs = WCS(header)

        # A SHEImage object to play with
        self.w = 50
        self.h = 20
        array = np.random.randn(self.w * self.h).reshape((self.w, self.h))
        self.img = SHEImage(array, header = header, wcs = self.wcs)

        # Set up qualified filenames to test
        self.qualified_test_filename = get_qualified_filename(self.TEST_FILENAME, self.workdir)
        self.l_qualified_test_filenames = [get_qualified_filename(filename, self.workdir)
                                           for filename in self.L_TEST_FILENAMES]

        # Clean up any test files that might have been left behind by a previous test
        self.cleanup()

    def teardown(self):
        """Override teardown to cleanup any created files.
        """

        self.cleanup()

    def cleanup(self):
        """Cleanup any created test files.
        """

        for qualified_filename in self.l_qualified_test_filenames + [self.qualified_test_filename]:
            if os.path.exists(qualified_filename):
                os.remove(qualified_filename)

    def test_init(self):
        """Test that the object created by setup_class is as expected.
        """

        assert self.img.shape == (self.w, self.h)
        assert self.img.data.shape == self.img.shape

        assert self.img.mask.shape == self.img.shape
        assert self.img.noisemap is None
        assert self.img.segmentation_map is None
        assert self.img.background_map is None
        assert self.img.weight_map is None

    def test_data_property(self):
        """Test that the `data` property behaves as expected, for its unique behaviours
        """

        img_copy = deepcopy(self.img)

        # ValueError if setting to an array of improper dimensions
        with pytest.raises(ValueError):
            img_copy.data = np.zeros((self.w,))
        with pytest.raises(ValueError):
            img_copy.data = np.zeros((self.w, self.h, self.w))

        # ValueError if try to modify shape
        with pytest.raises(ValueError):
            img_copy.data = np.zeros((self.w, self.h + 1))

    def test_attr_properties(self):
        """Test that the various `attr` properties behave as expected.
        """

        for attr_name, attr in D_ATTR_CONVERSIONS.items():

            img_copy = deepcopy(self.img)

            setattr(img_copy, attr, np.zeros((self.w, self.h), dtype = D_IMAGE_DTYPES[attr_name]))
            a = getattr(img_copy, attr)
            a += 1
            assert np.allclose(getattr(img_copy, attr), np.ones((self.w, self.h)))

            # Test we can delete it
            delattr(img_copy, attr)
            assert getattr(img_copy, attr) is None

    def test_header_wcs_properties(self):
        """Test that the `header`, `wcs`, and `galsim_wcs` properties behave as expected.
        """

        img_copy = deepcopy(self.img)

        # TypeError if setting to an improper type
        with pytest.raises(TypeError):
            img_copy.header = {"foo": "bar"}
        with pytest.raises(TypeError):
            img_copy.wcs = img_copy.galsim_wcs

        # Check that GalSim WCS, based on this header
        assert img_copy.galsim_wcs is not None

        # Check that deleting the header works as expected
        del img_copy.header
        del img_copy.wcs
        assert img_copy.header is None
        assert img_copy.wcs is None

        # GalSim WCS should also be deleted now
        with pytest.raises(ValueError):
            _ = img_copy.galsim_wcs

        # Now do some tests of the GalSim WCS
        # Start with a fresh copy of the image
        img_copy = deepcopy(self.img)

        # TypeError if setting to an improper type
        with pytest.raises(TypeError):
            img_copy.galsim_wcs = img_copy.wcs

        # Test deletion of the GalSim WCS

        # Can recreate if wcs still exists
        del img_copy.galsim_wcs
        del img_copy.header
        assert img_copy.galsim_wcs is not None

        # Can't recreate without wcs
        del img_copy.wcs
        del img_copy.header
        del img_copy.galsim_wcs
        with pytest.raises(ValueError):
            _ = img_copy.galsim_wcs

    def test_mask(self):
        """Tests some mask functionality.
        """

        img = deepcopy(self.img)

        # Add a default mask and check its data type and values
        img.add_default_mask(force = True)
        assert img.mask.dtype == np.int32
        assert img.mask[5, 5] == 0
        assert bool(img.boolmask[5, 5]) is False
        assert img.mask.shape == (self.w, self.h)

        # Check that boolmask works if we change the mask
        img.mask[5, 5] = 100
        assert bool(img.boolmask[5, 5]) is True

        # Check that non-forcibly adding a default mask doesn't affect the existing mask
        img.add_default_mask(force = False)
        assert bool(img.boolmask[5, 5]) is True

        # Check that forcibly adding a default mask does affect the existing mask
        img.add_default_mask(force = True)
        assert bool(img.boolmask[5, 5]) is False

        # Check that boolmask is None if mask is None
        del img.mask
        assert img.boolmask is None

    def test_noisemap(self):
        """Test that the noisemap behaves appropriately.
        """

        img = deepcopy(self.img)

        # Add a default noisemap and check its data type and values
        img.add_default_noisemap(force = True)
        assert img.noisemap.dtype == NOISEMAP_DTYPE
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
        """Test that the segmentation map behaves appropriately.
        """

        img = deepcopy(self.img)

        # Add a default segmentation_map and check its data type and values
        img.add_default_segmentation_map(force = True)
        assert img.segmentation_map.dtype == SEG_DTYPE
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
        """Test that the weight_map behaves appropriately.
        """

        img = deepcopy(self.img)

        # Add a default weight_map and check its data type and values
        img.add_default_weight_map(force = True)
        assert img.weight_map.dtype == WGT_DTYPE
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
        """Test the header behaves as expected.
        """

        img = deepcopy(self.img)

        img.add_default_header(force = True)

        img.header["temp1"] = (22.3, "Outside temp in degrees Celsius")
        img.header["INSTR"] = "DMK21"
        img.header.set("tel", "14-inch Martini Dobson")

        # Confirm capitalization does not matter
        assert img.header["TEMP1"] > 20.0
        assert len(img.header["INSTR"]) == 5

        # Check that non-forcibly adding a default header doesn't affect the existing header
        img.add_default_header(force = False)
        assert "INSTR" in img.header

        # Check that forcibly adding a default header does affect the existing header
        img.add_default_header(force = True)
        assert "INSTR" not in img.header

    def test_wcs_default(self):
        """Test the default WCS behaves as expected.
        """

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

    def test_shape_property(self):
        """Test the shape property behaves as expected.
        """

        img = deepcopy(self.img)

        assert img.shape == (self.w, self.h)

        # Disallow setting unless images aren't loaded
        with pytest.raises(ValueError):
            img.shape = (self.w, self.h)
        del img.data
        img.shape = (self.w, self.h + 1)
        assert np.all(img.shape == (self.w, self.h + 1))

        # Test deletion
        del img.shape
        assert np.all(img.shape == DETECTOR_SHAPE)

    def test_det_ixy(self):
        """Test that the properties for detector x and y position behave as expected.
        """

        img = deepcopy(self.img)

        # Test with no header - will default to detector 1-1
        del img.header
        assert img.det_ix == 1
        assert img.det_iy == 1

        # Try putting the values in the header in both possible formats. Note that the header stores them in the
        # order Y-X
        img.add_default_header()
        img.header[CCDID_LABEL] = "3-2"

        img.det_ix = None
        assert img.det_ix == 2
        img.det_iy = None
        assert img.det_iy == 3

        # And check det_iy generates both as well
        img.det_iy = None
        assert img.det_iy == 3

        img.det_ix = None
        img.det_iy = None
        img.header[CCDID_LABEL] = "5-4"
        assert img.det_ix == 4
        assert img.det_iy == 5

        # Try to set it to something other than what's in the header
        img.det_ix = 6
        img.det_iy = 1
        assert img.det_ix == 6
        assert img.det_iy == 1

    def test_parent_properties(self):
        """Test that the parent properties work as expected.
        """

        img = deepcopy(self.img)

        # Check that we get None if set to None
        img.parent_frame_stack = None
        img.parent_frame = None
        img.parent_image_stack = None
        img.parent_image = None

        assert img.parent_frame_stack is None
        assert img.parent_frame is None
        assert img.parent_image_stack is None
        assert img.parent_image is None

        # Check that we get the object we set to. We set each parent to a different deepcopy of this image,
        # since we need something we can create a weak reference to, and will just be checking identity,
        # so this image works for that
        mock_parent_frame_stack = deepcopy(img)
        mock_parent_frame = deepcopy(img)
        mock_parent_image_stack = deepcopy(img)
        mock_parent_image = deepcopy(img)

        img.parent_frame_stack = mock_parent_frame_stack
        img.parent_frame = mock_parent_frame
        img.parent_image_stack = mock_parent_image_stack
        img.parent_image = mock_parent_image

        assert img.parent_frame_stack is mock_parent_frame_stack
        assert img.parent_frame is mock_parent_frame
        assert img.parent_image_stack is mock_parent_image_stack
        assert img.parent_image is mock_parent_image

        # Check that the deleter sets each parent back to None
        del img.parent_frame_stack
        del img.parent_frame
        del img.parent_image_stack
        del img.parent_image

        assert img.parent_frame_stack is None
        assert img.parent_frame is None
        assert img.parent_image_stack is None
        assert img.parent_image is None

    def test_fits_read_write(self):
        """We save the small SHEImage, read it again, and compare both versions.
        """

        img = deepcopy(self.img)

        # To have a non-trivial image, we tweak it a bit:
        img.noisemap = 1.0 + 0.01 * np.random.randn(self.w * self.h).reshape((self.w, self.h))
        img.add_default_mask()
        img.mask[0:10, :] = 1
        img.mask[10:20, :] = 255
        # The below will get converted and should not prevent the test from working
        img.mask[30:40, :] = -10456.34
        img.add_default_segmentation_map()
        img.segmentation_map[10:20, 20:30] = 1

        img.wcs = self.wcs

        img.write_to_fits(self.qualified_test_filename, overwrite = False)

        read_img = SHEImage.read_from_fits(self.qualified_test_filename)

        assert np.allclose(img.data, read_img.data)
        assert np.allclose(img.mask, read_img.mask)
        assert np.allclose(img.noisemap, read_img.noisemap)
        assert np.allclose(img.segmentation_map, read_img.segmentation_map)

        # Check the wcs behaves the same
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            # Note - not testing here that we recover proper ra/dec or x/y, since that's covered in separate test
            # Just testing WCS from writing/reading is the same here

            ra1, dec1 = img.pix2world(x, y, origin = 1)
            ra2, dec2 = read_img.pix2world(x, y, origin = 1)

            assert np.allclose((ra1, dec1), (ra2, dec2))

            x1, y1 = img.world2pix(ra, dec, origin = 1)
            x2, y2 = read_img.world2pix(ra, dec, origin = 1)

            assert np.allclose((x1, y1), (x2, y2))

        # Also check the transformation matrices match up
        assert np.allclose(img.get_world2pix_transformation(0, 0),
                           read_img.get_world2pix_transformation(0, 0))
        assert np.allclose(img.get_pix2world_transformation(0, 0),
                           read_img.get_pix2world_transformation(0, 0))

        # Test writing with header but no WCS
        del img.wcs
        img.header["FOO"] = "BAR"
        img.write_to_fits(self.qualified_test_filename, overwrite = True)
        read_img = SHEImage.read_from_fits(self.qualified_test_filename)
        assert read_img.header["FOO"] == "BAR"

    def test_read_from_fits_files(self):
        """At least a small test of reading from individual FITS files.
        """

        img = SHEImage(np.random.randn(100).reshape(10, 10) + 200.0)
        img.mask = np.ones_like(img.data, dtype = np.int32)
        img.noisemap = 1.0 + 0.01 * np.random.randn(100).reshape(10, 10)
        img.write_to_fits(self.l_qualified_test_filenames[0])

        img.mask[:, :] = 2
        img.write_to_fits(self.l_qualified_test_filenames[1])

        img.noisemap = 1000.0 + 0.01 * np.random.randn(100).reshape(10, 10)
        img.write_to_fits(self.l_qualified_test_filenames[2])

        img.segmentation_map = 4 * np.ones_like(img.data, dtype = np.int32)
        img.write_to_fits(self.l_qualified_test_filenames[3])

        read_img = SHEImage.read_from_fits(self.l_qualified_test_filenames[0])
        assert read_img.mask[0, 0] == 1

        read_img = SHEImage.read_from_fits(self.l_qualified_test_filenames[0],
                                           mask_filepath = self.l_qualified_test_filenames[1],
                                           noisemap_filepath = self.l_qualified_test_filenames[2],
                                           segmentation_map_filepath = self.l_qualified_test_filenames[3])
        assert read_img.noisemap[0, 0] > 500.0
        assert read_img.segmentation_map[0, 0] == 4

        # As the primary HDU of mask_filepath is not an int, this will fail:
        with pytest.raises(TypeError):
            _ = SHEImage.read_from_fits(self.l_qualified_test_filenames[0],
                                        mask_filepath = self.l_qualified_test_filenames[1],
                                        noisemap_filepath = self.l_qualified_test_filenames[2],
                                        segmentation_map_filepath = self.l_qualified_test_filenames[
                                            3],
                                        mask_ext = PRIMARY_TAG)

    def test_extracted_stamp_is_view(self):
        """Checks that the extracted stamp is a view, not a copy.
        """

        # central pixel of stamp is index [10, 10] of the big array
        stamp = self.img.extract_stamp(10.5, 10.5, 3)
        # the central pixel, modified both here and in img
        stamp.data[1, 1] = -50.0

        assert self.img.data[10, 10] == stamp.data[1, 1]

    def test_extract_stamp_not_square(self):
        """Testing that non-square stamps are correctly extracted.
        """

        stamp = self.img.extract_stamp(10.0, 10.0, 5)
        assert stamp.shape == (5, 5)
        stamp = self.img.extract_stamp(10.0, 10.0, 4, 6)
        assert stamp.shape == (4, 6)

    def test_extract_stamp_indexconvs(self):
        """Test the effect of different indexconvs.
        """

        bl_pix_numpy = self.img.extract_stamp(0.5, 0.5, 1)
        bl_pix_sex = self.img.extract_stamp(1.0, 1.0, 1, indexconv = "sextractor")
        assert bl_pix_numpy.data == bl_pix_sex.data

    def test_extract_stamp(self):
        """We test that the stamp extraction get the correct data.
        """

        size = 64
        array = np.random.randn(size ** 2).reshape((size, size))
        array[0:32, 0:32] = 1.0e15  # bottom-left stamp is high and constant

        img = SHEImage(array)

        img.add_default_mask()
        img.mask[32:64, :] = True

        img.noisemap = 1000.0 + np.random.randn(size ** 2).reshape((size, size))

        img.add_default_segmentation_map()
        img.segmentation_map[0:32, :] = 1
        img.segmentation_map[32:64, :] = 2

        img.add_default_header()
        img.header["foo"] = "bar"

        # Testing extracted shape and extracted mask
        extracted_img = img.extract_stamp(16.4, 15.6, 32)
        assert extracted_img.shape == (32, 32)
        # Nothing should be masked
        assert np.sum(extracted_img.mask) == 0
        # Should all belong to object 1
        assert np.sum(extracted_img.segmentation_map) == 1 * np.product(extracted_img.shape)
        assert np.std(extracted_img.data) < 1.0e-10
        assert 900.0 < np.mean(extracted_img.noisemap) < 1100.0

        extracted_img = img.extract_stamp(32 + 16.4, 32 + 15.6, 32)
        assert extracted_img.shape == (32, 32)
        # This one is fully masked
        assert np.sum(extracted_img.mask) == 1 * np.product(extracted_img.shape)
        # Should all belong to object 2
        assert np.sum(extracted_img.segmentation_map) == 2 * np.product(extracted_img.shape)
        assert np.std(extracted_img.data) > 1.0e-10

        # And the header:
        extracted_img = img.extract_stamp(5, 5, 5)
        assert extracted_img.header is None
        extracted_img = img.extract_stamp(5, 5, 5, keep_header = True)
        assert len(list(extracted_img.header.keys())) == 1  # The "foo"

        # Test setting or not setting default properties for an extracted stamp
        simple_img = SHEImage(array)

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
        """We test that the stamp extraction works as desired for stamps not entirely within the image.
        """

        array = np.array([[0, 1, 2, 3, 4], [10, 11, 12, 13, 14], [20, 21, 22, 23, 24], [30, 31, 32, 33, 34]])
        img = SHEImage(array)
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
        assert bool(stamp.boolmask[1, 1]) is False
        assert bool(stamp.boolmask[0, 0]) is True

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
        assert bool(stamp.boolmask[2, 0]) is True

        # Check that none_if_out_of_bounds works correctly
        stamp = img.extract_stamp(-1000, -1000, 10, none_if_out_of_bounds = True)
        assert stamp is None

    def test_extract_wcs_stamp(self):
        """Test that extracting a WCS-only stamp behaves as expected.
        """

        offset_x = 10
        offset_y = 20

        # Testing extracted shape and extracted mask
        extracted_img = self.img.extract_wcs_stamp(offset_x, offset_y)

        # Check that the offset is correct
        assert np.all(extracted_img.offset == (offset_x, offset_y))

        # Check that all properties aside from header and WCS are None or other appropriate null value
        assert extracted_img.data.shape == (0, 0)
        assert extracted_img.mask is None
        assert extracted_img.noisemap is None
        assert extracted_img.segmentation_map is None
        assert extracted_img.background_map is None
        assert extracted_img.weight_map is None

        # Check that we inherit appropriate attributes from the parent
        assert extracted_img.wcs is self.img.wcs
        assert extracted_img.header is self.img.header
        assert extracted_img.parent_frame_stack is self.img.parent_frame_stack
        assert extracted_img.parent_frame is self.img.parent_frame
        assert extracted_img.parent_image_stack is self.img.parent_image_stack

        # Check that the parent image is set appropriately
        assert extracted_img.parent_image is self.img

        # Check that none_if_out_of_bounds works correctly
        stamp = self.img.extract_wcs_stamp(-1000, -1000, none_if_out_of_bounds = True)
        assert stamp is None

    def test_offset(self):
        """Testing the offset property.
        """

        size = 64
        array = np.random.randn(size ** 2).reshape((size, size))
        img = SHEImage(array)

        # Testing expected behavior of stamp extraction
        stamp = img.extract_stamp(2.5, 3.5, 1)
        assert stamp.offset[0] == 2
        assert stamp.offset[1] == 3

        # Does it survive FITS io?
        stamp.write_to_fits(self.qualified_test_filename, overwrite = True)
        read_stamp = SHEImage.read_from_fits(self.qualified_test_filename)
        assert read_stamp.offset[0] == 2
        assert read_stamp.offset[1] == 3

        # ValueError if setting to something where length is not 2
        with pytest.raises(ValueError):
            stamp.offset = [1]
        with pytest.raises(ValueError):
            stamp.offset = [1, 2, 3]

    def test_get_object_mask(self):
        """Test that the get_object_mask function behaves as expected.
        """

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
        img = SHEImage(data = np.zeros_like(mask),
                       mask = mask,
                       segmentation_map = segmap)

        # Test for various possible cases

        # Don't mask suspect or unassigned
        desired_bool_mask = np.array(((False, False, True),
                                      (False, False, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert np.all(img.get_object_mask(1, mask_suspect = False, mask_unassigned = False)
                      == desired_bool_mask)

        # Mask suspect, not unassigned
        desired_bool_mask = np.array(((False, True, True),
                                      (False, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert np.all(img.get_object_mask(1, mask_suspect = True, mask_unassigned = False)
                      == desired_bool_mask)

        # Mask unassigned, not suspect
        desired_bool_mask = np.array(((False, False, True),
                                      (True, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert np.all(img.get_object_mask(1, mask_suspect = False, mask_unassigned = True)
                      == desired_bool_mask)

        # Mask suspect and unassigned
        desired_bool_mask = np.array(((False, True, True),
                                      (True, True, True),
                                      (True, True, True)),
                                     dtype = bool)

        assert np.all(img.get_object_mask(1, mask_suspect = True, mask_unassigned = True)
                      == desired_bool_mask)

        # Test we get expected errors
        del img.mask
        with pytest.raises(ValueError):
            img.get_object_mask(1)
        img.add_default_mask()
        del img.segmentation_map
        with pytest.raises(ValueError):
            img.get_object_mask(1)

    def test_pix2world2pix(self):
        """Test that pix2world and world2pix work properly"""

        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            ra0, dec0 = self.img.pix2world(x + 1, y + 1, origin = 0)
            assert np.allclose((ra0, dec0), (ra, dec))

            ra1, dec1 = self.img.pix2world(x, y, origin = 1)
            assert np.allclose((ra1, dec1), (ra, dec))

            x0, y0 = self.img.world2pix(ra, dec, origin = 0)
            assert np.allclose((x0 + 1, y0 + 1), (x, y))

            x1, y1 = self.img.world2pix(ra, dec, origin = 1)
            assert np.allclose((x1, y1), (x, y))

        # Test that we get an expected exception if the WCS isn't set up
        img = deepcopy(self.img)
        del img.wcs, img.galsim_wcs, img.header
        with pytest.raises(AttributeError):
            _ = img.pix2world(0, 0)
        with pytest.raises(AttributeError):
            _ = img.world2pix(0, 0)

    def test_transformations(self):
        """Test that the transformations work properly.
        """

        # Check that the transformations are approximately the inverses of each other

        for spatial_ra in (False, True):
            for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                                  (24, 38, 52.53677316085, -28.75899827058671),
                                  (1012, 4111, 52.876229370322626, -28.686527560717373),
                                  (None, None, None, None)):

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

                # Skip detailed tests in cases where it's unnecessary
                if spatial_ra or x is None:
                    continue

                # Check that these can be applied successfully
                dx = 2.0
                dy = 0.5

                new_ra_dec = np.array([[ra], [dec]]) + pix2world_transformation @ np.array([[dx], [dy]])
                new_ra = new_ra_dec[0, 0]
                new_dec = new_ra_dec[1, 0]

                assert np.allclose((new_ra, new_dec), self.img.pix2world(x + dx, y + dy),
                                   rtol = 1e-5, atol = 1e-4)

                dra = 2.0 / 3600
                ddec = 0.5 / 3600

                new_xy = np.array([[x], [y]]) + world2pix_transformation @ np.array([[dra], [ddec]])
                new_x = new_xy[0, 0]
                new_y = new_xy[1, 0]

                assert np.allclose((new_x, new_y), self.img.world2pix(ra + dra, dec + ddec, origin = 1),
                                   rtol = 1e-2, atol = 1e-4)

        # Check that we get expected errors

        # ValueError if dx==0 or dy==0 for get_pix2world_transformation
        with pytest.raises(ValueError):
            _ = self.img.get_pix2world_transformation(x = None, y = None, dx = 0)
        with pytest.raises(ValueError):
            _ = self.img.get_pix2world_transformation(x = None, y = None, dy = 0)

        # ValueError if dra==0 or ddec==0 for get_world2pix_transformation
        with pytest.raises(ValueError):
            _ = self.img.get_world2pix_transformation(ra = None, dec = None, dra = 0)
        with pytest.raises(ValueError):
            _ = self.img.get_world2pix_transformation(ra = None, dec = None, ddec = 0)

        # ValueError if only one of ra and dec is None
        with pytest.raises(ValueError):
            _ = self.img.get_world2pix_transformation(ra = 0, dec = None)
        with pytest.raises(ValueError):
            _ = self.img.get_world2pix_transformation(ra = None, dec = 0)

    def test_rotation(self):
        """Test that the rotation works properly.
        """

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
                pix2world_angle = estimate_pix2world_rotation_angle(self.img,
                                                                    x = x,
                                                                    y = y,
                                                                    dx = dx,
                                                                    dy = dy,
                                                                    origin = 1)
                if pix2world_angle < 0:
                    pix2world_angle += 2 * np.pi
                elif pix2world_angle > 2 * np.pi:
                    pix2world_angle -= 2 * np.pi

                world2pix_angle = estimate_world2pix_rotation_angle(self.img,
                                                                    ra = ra,
                                                                    dec = dec,
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
        """Test that we can generate and use a GalSim-style WCS.
        """

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
            ra_dec_pos = img.galsim_wcs.toWorld(galsim.PositionD(x, y))
            # Need to divide out units for numpy to understand the values
            assert np.allclose((ra_dec_pos.ra / galsim.degrees, ra_dec_pos.dec / galsim.degrees), (ra, dec))

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
            ra_dec_pos = img.galsim_wcs.toWorld(galsim.PositionD(x, y))
            # Need to divide out units for numpy to understand the values
            assert np.allclose((ra_dec_pos.ra / galsim.degrees, ra_dec_pos.dec / galsim.degrees), (ra, dec))

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
        """Test that we can get the expected local decomposition of a WCS.
        """

        # Test with values coming from calculation assuming origin=1
        for x, y, ra, dec in ((0, 0, 52.53373984070186, -28.760675854311447),
                              (24, 38, 52.53677316085, -28.75899827058671),
                              (1012, 4111, 52.876229370322626, -28.686527560717373)):

            w2p_scale, _, w2p_angle, w2p_flip = self.img.get_world2pix_decomposition(ra, dec)
            p2w_scale, _, p2w_angle, p2w_flip = self.img.get_pix2world_decomposition(x, y)

            # Check the scales are inverses
            assert np.isclose(w2p_scale, 1. / p2w_scale)

            # Shear is checked for the non-celestial WCS

            # Check the angles are opposite (need to divide out units for numpy to understand the values)
            assert np.isclose(w2p_angle / galsim.degrees, - p2w_angle / galsim.degrees)

            # Check the flip is the same
            assert w2p_flip == p2w_flip

            # Check the angle matches what we get in the rotation matrix
            pix2world_rotation_matrix = self.img.get_pix2world_rotation(x, y, origin = 1)
            assert np.isclose(p2w_angle.cos(), pix2world_rotation_matrix[0, 0], rtol = 1e-4)
            assert np.isclose(p2w_angle.sin(), pix2world_rotation_matrix[0, 1], rtol = 1e-4)

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

    def test_get_objects_in_detector(self):
        """Unit test of the `get_objects_in_detector` method.
        """

        # We set up points to test first based on pixel coords, since we can tell easily what's in or not

        # Set up lists, using each possible combination of each x and y test point
        base_len = 6
        l_x = np.array([x for x in [-100, -1, 2, self.w - 2, self.w + 1, self.w + 100] for _ in range(base_len)])
        l_y = np.array([-100, -1, 2, self.h - 2, self.h + 1, self.h + 100] * base_len)

        l_ra, l_dec = self.img.pix2world(l_x, l_y, origin = 0)

        sc = SkyCoord(l_ra, l_dec, unit = 'deg')

        for x_buffer in (0, 5, -5):
            for y_buffer in (0, 5, -5):
                (l_indices_confirmed,
                 l_x_confirmed,
                 l_y_confirmed) = self.img.get_objects_in_detector(sc,
                                                                   x_buffer = x_buffer,
                                                                   y_buffer = y_buffer,
                                                                   origin = 0)

                # Do a manual check of in-bounds-ness, which we'll use for comparison
                l_in_bounds: np.ndarray[bool] = np.logical_and.reduce(((-x_buffer <= l_x),
                                                                       (l_x <= self.w - 1 + x_buffer),
                                                                       (-y_buffer <= l_y),
                                                                       (l_y <= self.h - 1 + y_buffer)))

                # Check that the results are as expected
                buffer_str = f"{x_buffer=}, {y_buffer=}"
                assert np.all(l_indices_confirmed == np.where(l_in_bounds)[0]), buffer_str
                assert np.allclose(l_x_confirmed, l_x[l_in_bounds]), buffer_str
                assert np.allclose(l_y_confirmed, l_y[l_in_bounds]), buffer_str

        # Test the 'origin' kwarg behaves as expected by setting it to 1, and checking that the result x and y
        # increase by 1
        (l_indices_confirmed,
         l_x_confirmed,
         l_y_confirmed) = self.img.get_objects_in_detector(sc,
                                                           x_buffer = 0,
                                                           y_buffer = 0,
                                                           origin = 1)
        l_in_bounds: np.ndarray[bool] = np.logical_and.reduce(((0 <= l_x),
                                                               (l_x <= self.w - 1),
                                                               (0 <= l_y),
                                                               (l_y <= self.h - 1)))
        assert np.all(l_indices_confirmed == np.where(l_in_bounds)[0])
        assert np.allclose(l_x_confirmed, l_x[l_in_bounds] + 1)
        assert np.allclose(l_y_confirmed, l_y[l_in_bounds] + 1)

    def test_equality(self):
        """Test of the custom __eq__ method for equality comparisons.
        """

        # Test we get equal when we expect it
        img_copy = deepcopy(self.img)
        assert self.img == img_copy

        # Test we get unequal when we change the copy
        img_copy.data += 1
        assert self.img != img_copy
