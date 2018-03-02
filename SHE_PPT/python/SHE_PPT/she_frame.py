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

Created on: 02/03/17
"""

from SHE_PPT import magic_values as mv
from SHE_PPT import products
import SHE_PPT.detector
from SHE_PPT.she_image_data import SHEImageData
from SHE_PPT.utility import find_extension
from astropy.wcs import WCS
import numpy as np

from . import logging


logger = logging.getLogger( __name__ )


class SHEFrame( object ):  # We need new-style classes for properties, hence inherit from object
    """Structure containing an array of SHEImageData objects, representing either an individual exposure or the stacked frame

    Attributes
    ----------
    detectors : 2D array (normally 6x6, but can be otherwise if needed)

    """

    def __init__( self, detectors ):
        """
        Parameters
        ----------
        detectors : dict (tuple<int,int> : SHEImageData)
            Dictionary of the detector data

        """

        self.detectors = detectors

    @classmethod
    def read( cls, frame_product_filename, bkg_product_filename, seg_product_filename, **kwargs ):
        """Reads a SHEFrame from disk


        Parameters
        ----------
        frame_product_filename : str
            Filename of the CalibratedFrame or StackedFrame data product
        bkg_product_filename : str
            Filename of the VisFlatFrame (background) data product
        seg_product_filename : str
            Filename of the Mosaic (segmentation map) data product
        psf_product_filename : str
            Filename of the PSFImage data product

        Any kwargs are passed to the reading of the SHEImageData
        """

        detectors = {}

        # Load in the relevant fits files

        # Load in the data from the primary frame
        frame_prod = read_xml_product( frame_product_filename )
        if not ( isinstance( frame_prod, products.calibrated_frame.DpdSheCalibratedFrameProduct ) or
                isinstance( frame_prod, products.calibrated_frame.DpdSheStackedFrameProduct ) ):
            raise ValueError( "Data image product from " +
                             frame_product_filename + " is invalid type." )

        frame_data_filename = join( workdir, frame_prod.get_filename() )

        frame_data_hdulist = fits.open( 
            frame_data_filename, mode = "readonly", memmap = True )

        # Load in the data from the background frame
        bkg_prod = read_xml_product( bkg_product_filename )
        if not isinstance( bkg_prod, products.background_frame.DpdSheBackgroundFrameProduct ):
            raise ValueError( "Data image product from " +
                             bkg_product_filename + " is invalid type." )

        bkg_data_filename = join( workdir, bkg_prod.get_filename() )

        bkg_data_hdulist = fits.open( 
            bkg_data_filename, mode = "readonly", memmap = True )

        # Load in the data from the segmentation frame
        seg_prod = read_xml_product( seg_product_filename )
        if not isinstance( seg_prod, products.segmentation_frame.DpdSheSegmentationFrameProduct ):
            raise ValueError( "Data image product from " +
                             seg_product_filename + " is invalid type." )

        seg_data_filename = join( workdir, seg_prod.get_filename() )

        seg_data_hdulist = fits.open( 
            seg_data_filename, mode = "readonly", memmap = True )

        for x_i in np.linspace( 1, 6, 6, dtype = int ):
            for y_i in np.linspace( 1, 6, 6, dtype = int ):

                id_string = SHE_PPT.detector.get_id_string( x_i, y_i )

                sci_extname = mv.sci_tag + "." + id_string
                sci_i = find_extension( frame_data_hdulist, sci_extname )

                noisemap_extname = mv.noisemap_tag + "." + id_string
                noisemap_i = find_extension( frame_data_hdulist, noisemap_extname )

                mask_extname = mv.mask_tag + "." + id_string
                mask_i = find_extension( frame_data_hdulist, mask_extname )

                bkg_extname = mv.segmentation_tag + "." + id_string
                bkg_i = find_extension( bkg_data_hdulist, bkg_extname )

                seg_extname = mv.segmentation_tag + "." + id_string
                seg_i = find_extension( seg_data_hdulist, seg_extname )

                detectors[( x_i, y_i )] = SHEImage( data = frame_data_hdulist[sci_i].data,
                                                    mask = frame_data_hdulist[noisemap_i].data,
                                                    noisemap = frame_data_hdulist[mask_i].data,
                                                    background_map = bkg_data_hdulist[bkg_i].data,
                                                    segmentation_map = seg_data_hdulist[seg_i].data,
                                                    header = frame_data_hdulist[sci_i].header,
                                                    wcs = WCS( frame_data_hdulist[sci_i].header ) )

        return SHEFrame( detectors )
