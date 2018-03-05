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
#

"""
File: python/SHE_PPT/she_frame.py

Created on: 02/03/18
"""

from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
import numpy as np
import os.path.join

import SHE_PPT.detector
from SHE_PPT.file_io import read_xml_product
from SHE_PPT import logging
from SHE_PPT import magic_values as mv
from SHE_PPT import products
from SHE_PPT.she_image import SHEImage
from SHE_PPT.table_formats.psf import tf as pstf
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import find_extension

logger = logging.getLogger( __name__ )


class SHEFrame( object ):  # We need new-style classes for properties, hence inherit from object
    """Structure containing an array of SHEImageData objects, representing either an individual exposure or the stacked frame

    Attributes
    ----------
    detectors : 2D array (normally 1-indexed 6x6, but can be otherwise if needed) of SHEImage objects
    bulge_psf_image : SHEImage
    disk_psf_image : SHEImage
    psf_catalogue : astropy.table.Table
        Table linking galaxy IDs to the positions of their corresponding psfs
    bulge_stamp_size : int
    disk_stamp_size : int

    """

    def __init__( self, detectors, bulge_psf_image, disk_psf_image, psf_catalogue ):
        """
        Parameters
        ----------
        detectors : 2D array (normally 1-indexed 6x6, but can be otherwise if needed) of SHEImage objects
        bulge_psf_image : SHEImage
        disk_psf_image : SHEImage
        psf_catalogue : astropy.table.Table
            Table linking galaxy IDs to the positions of their corresponding psfs
        """

        # Initialise directly
        self.detectors = detectors
        self.bulge_psf_image = bulge_psf_image
        self.disk_psf_image = disk_psf_image
        self.psf_catalogue = psf_catalogue
        
        # Get the stamp sizes for the bulge and disk psf images
        self.bulge_stamp_size = bulge_psf_image.header[mv.stamp_size_label]
        self.disk_stamp_size = disk_psf_image.header[mv.stamp_size_label]
        
        # Set the PSF catalogue to index by ID
        self.psf_catalogue.add_index(pstf.ID)
        
    def extract_stamp(self, x_world, y_world, width, height=None, x_buffer=0, y_buffer=0, keep_header=False):
        """Extracts a postage stamp centred on the provided sky co-ordinates, by using each detector's WCS
           to determine which (if any) it lies on. If x/y_buffer >0, it will also extract from a detector if
           the position is within this many pixels of the edge of it.
           
           Parameters
           ----------
           x_world : float
               The x sky co-ordinate (R.A.)
           y_world : float
               The y sky co-ordinate (Dec.)
           width : int
               The desired width of the postage stamp
           height : int
               The desired height of the postage stamp (default = width)
           x_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, x-dimension
           y_buffer : int
               The size of the buffer region in pixels around a detector to extract a stamp from, y-dimension
           keep_header : bool
               If True, will copy the detector's header to the stamp's
               
           Return
           ------
           stamp : SHEImage or None
               The extracted stamp, or None if it was not found on any detector
        """
        
        # Loop over the detectors, and use the WCS of each to determine if it's on it or not
        found = False
        
        num_x, num_y = np.shape(self.detectors)
        
        for x_i in range(num_x):
            for y_i in range(num_y):
                
                detector = self.detectors[x_i,y_i]
                if detector is None:
                    continue
                
                x, y = detector.world2pix(x_world,y_world)
                if (x < 1-x_buffer) or (x > np.shape(detector.data)[0]+x_buffer):
                    continue
                if (y < 1-y_buffer) or (y > np.shape(detector.data)[1]+y_buffer):
                    continue
                
                found = True
                
                break
        
            if found:
                break
            
        if detector is None:
            return None
            
        stamp = detector.extract_stamp(x=x,y=y,width=width,height=height,keep_header=keep_header)
        
        return stamp
    
    def extract_psf(self, gal_id, keep_header=False):
        
        row = self.psf_catalogue.loc[gal_id]
        
        psf_x = row[pstf.psf_x]
        psf_y = row[pstf.psf_y]
        
        bulge_psf_stamp = self.bulge_psf_image.extract_stamp(x=psf_x, y=psf_y,
                                                             width=self.bulge_stamp_size, keep_header=keep_header)
        disk_psf_stamp = self.bulge_psf_image.extract_stamp(x=psf_x, y=psf_y,
                                                            width=self.disk_stamp_size, keep_header=keep_header)
        
        return bulge_psf_stamp, disk_psf_stamp

    @classmethod
    def read( cls, frame_product_filename, seg_product_filename, psf_product_filename,
              workdir=".", x_max = 6, y_max = 6, **kwargs ):
        """Reads a SHEFrame from disk


        Parameters
        ----------
        frame_product_filename : str
            Filename of the CalibratedFrame data product
        seg_product_filename : str
            Filename of the Mosaic (segmentation map) data product
        seg_product_filename : str
            Filename of the PSF Image data product
        workdir : str
            Work directory
        x_max : int
            Maximum x-coordinate of detectors
        y_max : int
            Maximum y-coordinate of detectors

        Any kwargs are passed to the reading of the fits data
        """

        detectors = np.ndarray((x_max+1,y_max+1),dtype=SHEImage)

        # Load in the relevant fits files

        # Load in the data from the primary frame
        frame_prod = read_xml_product( os.path.join( workdir, frame_product_filename ) )
        if not isinstance( frame_prod, products.calibrated_frame.DpdSheCalibratedFrameProduct ):
            raise ValueError( "Data image product from " +
                             frame_product_filename + " is invalid type." )

        frame_data_filename = os.path.join( workdir, frame_prod.get_filename() )

        frame_data_hdulist = fits.open( 
            frame_data_filename, mode = "denywrite", memmap = True )

        # Load in the data from the background frame
        bkg_data_filename = os.path.join( workdir, frame_prod.get_bkg_filename() )

        bkg_data_hdulist = fits.open( 
            bkg_data_filename, mode = "denywrite", memmap = True )

        # Load in the data from the segmentation frame
        seg_prod = read_xml_product( os.path.join( workdir, seg_product_filename ) )
        if not isinstance( seg_prod, products.mosaic.DpdMerMosaicProduct ):
            raise ValueError( "Data image product from " +
                             seg_product_filename + " is invalid type." )

        seg_data_filename = os.path.join( workdir, seg_prod.get_filename() )

        seg_data_hdulist = fits.open( 
            seg_data_filename, mode = "denywrite", memmap = True )

        for x_i in np.linspace( 1, x_max, x_max, dtype = int ):
            for y_i in np.linspace( 1, y_max, y_max, dtype = int ):

                id_string = SHE_PPT.detector.get_id_string( x_i, y_i )

                sci_extname = mv.sci_tag + "." + id_string
                sci_i = find_extension( frame_data_hdulist, sci_extname )
                if sci_i is None:
                    continue  # Don't raise here; might be just using limited number

                noisemap_extname = mv.noisemap_tag + "." + id_string
                noisemap_i = find_extension( frame_data_hdulist, noisemap_extname )
                if noisemap_i is None:
                    raise ValueError( "No corresponding noisemap extension found in file " + frame_data_filename + "." +
                                     "Expected extname: " + noisemap_extname )

                mask_extname = mv.mask_tag + "." + id_string
                mask_i = find_extension( frame_data_hdulist, mask_extname )
                if noisemap_i is None:
                    raise ValueError( "No corresponding mask extension found in file " + frame_data_filename + "." +
                                     "Expected extname: " + mask_extname )

                bkg_extname = mv.segmentation_tag + "." + id_string
                bkg_i = find_extension( bkg_data_hdulist, bkg_extname )
                if noisemap_i is None:
                    raise ValueError( "No corresponding background extension found in file " + frame_data_filename + "." +
                                     "Expected extname: " + bkg_extname )

                seg_extname = mv.segmentation_tag + "." + id_string
                seg_i = find_extension( seg_data_hdulist, seg_extname )
                if noisemap_i is None:
                    raise ValueError( "No corresponding segmentation extension found in file " + frame_data_filename + "." +
                                     "Expected extname: " + seg_extname )

                detectors[ x_i, y_i ] = SHEImage( data = frame_data_hdulist[sci_i].data,
                                                  mask = frame_data_hdulist[noisemap_i].data,
                                                  noisemap = frame_data_hdulist[mask_i].data,
                                                  background_map = bkg_data_hdulist[bkg_i].data,
                                                  segmentation_map = seg_data_hdulist[seg_i].data,
                                                  header = frame_data_hdulist[sci_i].header,
                                                  wcs = WCS( frame_data_hdulist[sci_i].header ) )

        # Load in the PSF data
        psf_prod = read_xml_product( os.path.join( workdir, psf_product_filename ) )
        if not isinstance( psf_prod, products.psf_image.DpdShePSFImageProduct ):
            raise ValueError( "PSF image product from " +
                             psf_product_filename + " is invalid type." )

        qualified_psf_data_filename = os.path.join( workdir, psf_prod.get_filename() )

        psf_data_hdulist = fits.open( 
            qualified_psf_data_filename, mode = "denywrite", memmap = True )
        
        bulge_psf_i = find_extension(psf_data_hdulist, mv.bulge_psf_tag)
        bulge_psf_image = SHEImage(data=psf_data_hdulist[bulge_psf_i].data,
                                   header=psf_data_hdulist[bulge_psf_i].header)
        
        disk_psf_i = find_extension(psf_data_hdulist, mv.disk_psf_tag)
        disk_psf_image = SHEImage(data=psf_data_hdulist[disk_psf_i].data,
                                  header=psf_data_hdulist[disk_psf_i].header)
        
        psf_cat_i = find_extension(psf_data_hdulist, mv.psf_cat_tag)
        psf_cat = Table.read( psf_data_hdulist[psf_cat_i] )
            
        if not is_in_format(psf_cat,pstf):
            raise ValueError("PSF table from " + qualified_psf_data_filename + " is in invalid format.")

        # Construct and return a SHEFrame object
        return SHEFrame( detectors = detectors,
                         bulge_psf_image = bulge_psf_image,
                         disk_psf_image = disk_psf_image,
                         psf_catalogue = psf_cat )
