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

"""
File: tests/python/she_image_test.py

Created on: 08/18/17
"""



import logging
import os
import pytest

from SHE_PPT import file_io
from SHE_PPT.magic_values import segmap_unassigned_value
import SHE_PPT.she_image
from SHE_PPT.wcsutil import WCS
import numpy as np


logging.basicConfig( level = logging.DEBUG )

class Test_she_image():


    @classmethod
    def setup_class( cls ):

        # A filename for testing the file-saving:
        cls.testfilepath = "test_SHEImage.fits"  # Will be deleted by teardown_class()
        # For some tests we need several files:
        cls.testfilepaths = ["test_SHEImage_0.fits", "test_SHEImage_1.fits", "test_SHEImage_2.fits",
                             "test_SHEImage_3.fits"]

        # A WCS to use (from the auxdir)
        header_file = file_io.find_file( "AUX/SHE_PPT/tpv_header.bin" )
        header = file_io.read_pickled_product( header_file )
        cls.wcs = WCS ( header )

        # A SHEImage object to play with
        cls.w = 50
        cls.h = 20
        array = np.random.randn( cls.w * cls.h ).reshape( ( cls.w, cls.h ) )
        cls.img = SHE_PPT.she_image.SHEImage( array, wcs = cls.wcs )

    @classmethod
    def teardown_class( cls ):

        # Delete all potentially created files:
        for testfilepath in cls.testfilepaths + [cls.testfilepath]:
            if os.path.exists( testfilepath ):
                os.remove( testfilepath )



    def test_init( self ):
        """Test that the object created by setup_class is as expected"""

        assert self.img.shape == ( self.w, self.h )
        assert self.img.data.shape == ( self.w, self.h )
        assert self.img.mask.shape == ( self.w, self.h )
        assert self.img.noisemap.shape == ( self.w, self.h )


    def test_mask( self ):
        """Tests some mask functionality"""

        self.img.mask[5, 5] = 100
        assert self.img.boolmask[5, 5] == True
        self.img.mask[5, 5] = 0
        assert self.img.boolmask[5, 5] == False
        assert self.img.mask.dtype == np.int32


    def test_segmentation_map( self ):
        """Test that the segmentation map is set up as all segmap_unassigned_value"""

        assert np.allclose( self.img.segmentation_map,
                           segmap_unassigned_value * np.ones_like( self.img.data, dtype = self.img.segmentation_map.dtype ) )


    def test_header( self ):
        """Modifying the header"""
        self.img.header["temp1"] = ( 22.3, "Outside temp in degrees Celsius" )
        self.img.header["INSTR"] = ( "DMK21" )
        self.img.header.set( "tel", "14-inch Martini Dobson" )

        assert self.img.header["TEMP1"] > 20.0  # capitalization does not matter
        assert len( self.img.header["INSTR"] ) == 5



    def test_fits_read_write( self ):
        """We save the small SHEImage, read it again, and compare both versions"""

        # To have a non-trivial image, we tweak it a bit:
        self.img.noisemap = 1.0 + 0.01 * np.random.randn( self.w * self.h ).reshape( ( self.w, self.h ) )
        self.img.mask[0:10, :] = 1
        self.img.mask[10:20, :] = 255
        self.img.mask[30:40, :] = -10456.34  # will get converted and should not prevent the test from working
        self.img.segmentation_map[10:20, 20:30] = 1

        self.img.wcs = self.wcs

        self.img.write_to_fits( self.testfilepath, clobber = False )

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepath )

        assert np.allclose( self.img.data, rimg.data )
        assert np.allclose( self.img.mask, rimg.mask )
        assert np.allclose( self.img.noisemap, rimg.noisemap )
        assert np.allclose( self.img.segmentation_map, rimg.segmentation_map )

        # Check the wcs behaves the same
        assert np.allclose( self.img.get_world2pix_transformation( 0, 0 ),
                           rimg.get_world2pix_transformation( 0, 0 ) )
        assert np.allclose( self.img.get_pix2world_transformation( 0, 0 ),
                           rimg.get_pix2world_transformation( 0, 0 ) )

        # We test that the header did not get changed # FIXME disabled for now
        # assert len(list(rimg.header.keys())) == 3
        # assert str(repr(self.img.header)) == str(repr(rimg.header))


    def test_read_from_separate_fits_files( self ):
        """At least a small test of reading from individual FITS files"""

        img = SHE_PPT.she_image.SHEImage( np.random.randn( 100 ).reshape( 10, 10 ) + 200.0 )
        img.mask[:, :] = 1
        img.noisemap = 1.0 + 0.01 * np.random.randn( 100 ).reshape( 10, 10 )
        img.write_to_fits( self.testfilepaths[0] )

        img.mask[:, :] = 2
        img.write_to_fits( self.testfilepaths[1] )

        img.noisemap = 1000.0 + 0.01 * np.random.randn( 100 ).reshape( 10, 10 )
        img.write_to_fits( self.testfilepaths[2] )

        img.segmentation_map[:, :] = 4
        img.write_to_fits( self.testfilepaths[3] )

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepaths[0] )
        assert rimg.mask[0, 0] == 1

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepaths[0],
                                                         mask_ext = None,
                                                         noisemap_ext = None,
                                                         segmentation_map_ext = None )
        assert rimg.mask[0, 0] == 0

        rimg = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepaths[0],
                                                         mask_filepath = self.testfilepaths[1],
                                                         noisemap_filepath = self.testfilepaths[2],
                                                         segmentation_map_filepath = self.testfilepaths[3] )
        assert rimg.noisemap[0, 0] > 500.0
        assert rimg.segmentation_map[0, 0] == 4

        with pytest.raises( ValueError ):  # As the primary HDU of mask_filepath is not a np.uint8, this will fail:
            rimg = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepaths[0],
                                                         mask_filepath = self.testfilepaths[1],
                                                         noisemap_filepath = self.testfilepaths[2],
                                                         segmentation_map_filepath = self.testfilepaths[3],
                                                         mask_ext = None )




    def test_extracted_stamp_is_view( self ):
        """Checks that the extracted stamp is a view, not a copy"""

        stamp = self.img.extract_stamp( 10.5, 10.5, 3 )  # central pixel of stamp is index [10, 10] of the big array
        stamp.data[1, 1] = -50.0  # the central pixel, modifed both here and in img

        assert self.img.data[10, 10] == stamp.data[1, 1]


    def test_extract_stamp_not_square( self ):
        """Testing that non-square stamps are correctly extracted"""

        stamp = self.img.extract_stamp( 10.0, 10.0, 5 )
        assert stamp.shape == ( 5, 5 )
        stamp = self.img.extract_stamp( 10.0, 10.0, 4, 6 )
        assert stamp.shape == ( 4, 6 )


    def test_extract_stamp_indexconvs( self ):
        """Test the effect of different indexconvs"""

        bottomleftpixel_numpy = self.img.extract_stamp( 0.5, 0.5, 1 )
        bottomleftpixel_sex = self.img.extract_stamp( 1.0, 1.0, 1, indexconv = "sextractor" )
        assert bottomleftpixel_numpy.data == bottomleftpixel_sex.data



    def test_extract_stamp( self ):
        """We test that the stamp extraction get the correct data"""

        size = 64
        array = np.random.randn( size ** 2 ).reshape( ( size, size ) )
        array[0:32, 0:32] = 1.0e15  # bottom-left stamp is high and constant
        img = SHE_PPT.she_image.SHEImage( array )
        img.mask[32:64, :] = True
        img.noisemap = 1000.0 + np.random.randn( size ** 2 ).reshape( ( size, size ) )
        img.segmentation_map[0:32, :] = 1
        img.segmentation_map[32:64, :] = 2
        img.header["foo"] = "bar"


        # Testing extracted shape and extracted mask
        eimg = img.extract_stamp( 16.4, 15.6, 32 )
        assert eimg.shape == ( 32, 32 )
        assert np.sum( eimg.mask ) == 0  # Nothing should be masked
        assert np.sum( eimg.segmentation_map ) == 1 * np.product( eimg.shape )  # Should all belong to object 1
        assert np.std( eimg.data ) < 1.0e-10
        assert np.mean( eimg.noisemap ) > 900.0 and np.mean( eimg.noisemap ) < 1100.0

        eimg = img.extract_stamp( 32 + 16.4, 32 + 15.6, 32 )
        assert eimg.shape == ( 32, 32 )
        assert np.sum( eimg.mask ) == 1 * np.product( eimg.shape )  # This one is fully masked
        assert np.sum( eimg.segmentation_map ) == 2 * np.product( eimg.shape )  # Should all belong to object 2
        assert np.std( eimg.data ) > 1.0e-10

        # And the header:
        eimg = img.extract_stamp( 5, 5, 5 )
        assert len( list( eimg.header.keys() ) ) == 2  # The two offsets
        eimg = img.extract_stamp( 5, 5, 5, keep_header = True )
        assert len( list( eimg.header.keys() ) ) == 3  # The offsets, and the "foo"


    def test_extract_stamp_out_of_bounds( self ):
        """We test that the stamp extraction works as desired for stamps not entirely within the image"""

        array = np.array( [[00, 0o1, 0o2, 0o3, 0o4], [10, 11, 12, 13, 14], [20, 21, 22, 23, 24], [30, 31, 32, 33, 34]] )
        img = SHE_PPT.she_image.SHEImage( array )
        # This image looks like (values give xy coords...)
        # 04 14 24 34
        # 03 13 23 33
        # 02 12 22 32
        # 01 11 21 31
        # 00 10 20 30

        stamp = img.extract_stamp( 0.5, 0.5, 3 )
        # This is:
        # XX 01 11
        # XX 00 10
        # XX XX XX
        assert stamp.data[2, 2] == 11
        assert stamp.data[2, 1] == 10
        assert stamp.data[0, 0] == 00
        assert stamp.boolmask[1, 1] == False
        assert stamp.boolmask[0, 0] == True

        stamp = img.extract_stamp( -10.0, 20.0, 3 )
        # This one is completely out of bounds:
        assert np.alltrue( stamp.boolmask )
        assert np.allclose( stamp.noisemap, 0.0 )
        assert np.allclose( stamp.segmentation_map, segmap_unassigned_value )

        stamp = img.extract_stamp( 3.5, 1.5, 3, 1 )
        # This is
        # 21 31 XX
        assert stamp.data[0, 0] == 21
        assert stamp.data[1, 0] == 31
        assert stamp.boolmask[2, 0] == True


    def test_offset( self ):
        """Testing the offset property"""

        size = 64
        array = np.random.randn( size ** 2 ).reshape( ( size, size ) )
        img = SHE_PPT.she_image.SHEImage( array )

        # Testing expected behavior of stamp extraction
        stamp = img.extract_stamp( 2.5, 3.5, 1 )
        assert stamp.offset[0] == 2
        assert stamp.offset[1] == 3

        # Does it survive FITS io?
        stamp.write_to_fits( self.testfilepath, clobber = True )
        rstamp = SHE_PPT.she_image.SHEImage.read_from_fits( self.testfilepath )
        assert rstamp.offset[0] == 2
        assert rstamp.offset[1] == 3



    def test_get_object_mask( self ):
        """Test that the get_object_mask function behaves as expected."""

        import SHE_PPT.mask as m

        # Create an object for testing
        mask = np.array( ( ( 0, m.masked_near_edge, m.masked_off_image ),
                         ( 0, m.masked_near_edge, m.masked_off_image ),
                         ( m.masked_bad_pixel, m.masked_near_edge, m.masked_off_image ) ),
                        dtype = np.int32 )

        segmap = np.array( ( ( 0, 0, 0 ),
                           ( segmap_unassigned_value, segmap_unassigned_value, segmap_unassigned_value ),
                           ( 1, 1, 1 ) ),
                          dtype = np.int32 )
        img = SHE_PPT.she_image.SHEImage( data = np.zeros_like( mask ),
                                         mask = mask,
                                         segmentation_map = segmap )

        # Test for various possible cases

        # Don't mask suspect or unassigned
        desired_bool_mask = np.array( ( ( False, False, True ),
                                      ( False, False, True ),
                                      ( True, True, True ) ),
                                     dtype = bool )

        assert ( img.get_object_mask( 0, mask_suspect = False, mask_unassigned = False )
                == desired_bool_mask ).all()

        # Mask suspect, not unassigned
        desired_bool_mask = np.array( ( ( False, True, True ),
                                      ( False, True, True ),
                                      ( True, True, True ) ),
                                     dtype = bool )

        assert ( img.get_object_mask( 0, mask_suspect = True, mask_unassigned = False )
                == desired_bool_mask ).all()

        # Mask unassigned, not suspect
        desired_bool_mask = np.array( ( ( False, False, True ),
                                      ( True , True, True ),
                                      ( True, True, True ) ),
                                     dtype = bool )

        assert ( img.get_object_mask( 0, mask_suspect = False, mask_unassigned = True )
                == desired_bool_mask ).all()

        # Mask suspect and unassigned
        desired_bool_mask = np.array( ( ( False, True, True ),
                                      ( True, True, True ),
                                      ( True, True, True ) ),
                                     dtype = bool )

        assert ( img.get_object_mask( 0, mask_suspect = True, mask_unassigned = True )
                == desired_bool_mask ).all()

    def test_pix2world( self ):
        """Test that pix2world works properly"""

        for x, y, ex_ra, ex_dec in ( ( 0, 0, 52.53373984070186, -28.760675854311447 ),
                                    ( 24, 38, 52.53677316085, -28.75899827058671 ),
                                    ( 1012, 4111, 52.876229370322626, -28.686527560717373 ) ):

            ra, dec = self.img.pix2world( x, y )

            assert np.allclose( ( ra, dec ), ( ex_ra, ex_dec ) )

    def test_world2pix( self ):
        """Test that world2pix works properly"""

        for ex_x, ex_y, ra, dec in ( ( 0, 0, 52.53373984070186, -28.760675854311447 ),
                                    ( 24, 38, 52.53677316085, -28.75899827058671 ),
                                    ( 1012, 4111, 52.876229370322626, -28.686527560717373 ) ):

            x, y = self.img.world2pix( ra, dec )

            assert np.allclose( ( x, y ), ( ex_x, ex_y ) )

    def test_transformations( self ):

        # Check that the transformations are approximately the inverses of each other

        for spatial_ra in ( False, True ):
            for x, y, ra, dec in ( ( 0, 0, 52.53373984070186, -28.760675854311447 ),
                                  ( 24, 38, 52.53677316085, -28.75899827058671 ),
                                  ( 1012, 4111, 52.876229370322626, -28.686527560717373 ) ):

                pix2world_transformation = self.img.get_pix2world_transformation( x, y, spatial_ra = spatial_ra )
                world2pix_transformation = self.img.get_world2pix_transformation( ra, dec, spatial_ra = spatial_ra )

                double_transformation = pix2world_transformation * world2pix_transformation

                assert np.allclose( double_transformation, np.matrix( [[1., 0.], [0., 1.]] ),
                                   rtol = 1e-2, atol = 1e-3 )

                if spatial_ra:
                    continue
                # Check that these can be applied successfully

                dx = 2.0
                dy = 0.5

                new_radec = np.matrix( [[ra], [dec]] ) + pix2world_transformation * np.matrix( [[dx], [dy]] )
                new_ra = new_radec[0, 0]
                new_dec = new_radec[1, 0]

                assert np.allclose( ( new_ra, new_dec ), self.img.pix2world( x + dx, y + dy ),
                                   rtol = 1e-5, atol = 1e-4 )

                dra = 2.0 / 3600
                ddec = 0.5 / 3600

                new_xy = np.matrix( [[x], [y]] ) + world2pix_transformation * np.matrix( [[dra], [ddec]] )
                new_x = new_xy[0, 0]
                new_y = new_xy[1, 0]

                assert np.allclose( ( new_x, new_y ), self.img.world2pix( ra + dra, dec + ddec ),
                                   rtol = 1e-2, atol = 1e-4 )

    def test_rotation( self ):

        for x, y, ra, dec in ( ( 0, 0, 52.53373984070186, -28.760675854311447 ),
                              ( 24, 38, 52.53677316085, -28.75899827058671 ),
                              ( 1012, 4111, 52.876229370322626, -28.686527560717373 ) ):

            # Get pix2world angles for each of a few different test steps
            pix2world_angles = []
            world2pix_angles = []
            for dx, dy in ( ( 0.1, 0.0 ),
                           ( 0.1, 0.1 ),
                           ( 0.0, 0.1 ),
                           ( -0.1, 0.1 ),
                           ( -0.1, 0.0 ),
                           ( -0.1, -0.1 ),
                           ( 0.0, -0.1 ),
                           ( 0.1, -0.1 ) ):
                pix2world_angle = self.img.estimate_pix2world_rotation_angle( x, y, dx = dx, dy = dy )
                if pix2world_angle < 0:
                    pix2world_angle += 2 * np.pi
                elif pix2world_angle > 2 * np.pi:
                    pix2world_angle -= 2 * np.pi

                world2pix_angle = self.img.estimate_world2pix_rotation_angle( ra, dec,
                                                                                dra = dx / 3600,
                                                                                ddec = dy / 3600 )
                if world2pix_angle < 0:
                    world2pix_angle += 2 * np.pi
                elif world2pix_angle > 2 * np.pi:
                    world2pix_angle -= 2 * np.pi

                pix2world_angles.append( pix2world_angle )
                world2pix_angles.append( world2pix_angle )

            # Get the mean for each, and check they're approximately opposites
            pix2world_angle = np.mean(pix2world_angles)
            world2pix_angle = np.mean(world2pix_angles)

            assert np.isclose(pix2world_angle,world2pix_angle+np.pi,rtol=0.05)
            
            # Now, create rotation matrices for both, and check these match what we get
            # from the SVD method
            pix2world_rotation_matrix_1 = np.matrix([[np.cos(pix2world_angle),-np.sin(pix2world_angle)],
                                                     [np.sin(pix2world_angle),np.cos(pix2world_angle)]])
            world2pix_rotation_matrix_1 = np.matrix([[np.cos(world2pix_angle),-np.sin(world2pix_angle)],
                                                     [np.sin(world2pix_angle),np.cos(world2pix_angle)]])

            pix2world_rotation_matrix_2 = self.img.get_pix2world_rotation( x, y )
            world2pix_rotation_matrix_2 = self.img.get_world2pix_rotation( ra, dec )
            
            assert np.allclose(pix2world_rotation_matrix_1,pix2world_rotation_matrix_2,rtol=0.02)
            assert np.allclose(world2pix_rotation_matrix_1,world2pix_rotation_matrix_2,rtol=0.02)
            
            return

