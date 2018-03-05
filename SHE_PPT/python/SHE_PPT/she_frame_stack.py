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
File: python/SHE_PPT/she_frame_stack.py

Created on: 05/03/18
"""

from astropy.io import fits
from astropy.table import Table
from astropy.wcs import WCS
import os.path.join

from SHE_PPT.file_io import read_listfile, read_xml_product
from SHE_PPT import logging
from SHE_PPT import magic_values as mv
from SHE_PPT import products
from SHE_PPT.she_frame import SHEFrame
from SHE_PPT.she_image import SHEImage
from SHE_PPT.table_formats.detections import tf as detf
from SHE_PPT.table_utility import is_in_format
from SHE_PPT.utility import find_extension

logger = logging.getLogger(__name__)

class SHEFrameStack(object): # We need new-style classes for properties, hence inherit from object
    """Structure containing all needed data shape measurement, represented as a list of SHEFrames for
    detector image data, a stacked image, a list of PSF images and catalogues, and a detections
    catalogue.
    
    Attributes
    ----------
    exposures : list<SHEImage>
        List of SHEImage objects representing the different exposures
    stacked_image : SHEImage
        The stacked image
    bulge_psf_images : list<SHEImage>
        List of bulge PSF images
    disk_psf_images : list<SHEImage>
        List of disk PSF images
    psf_catalogues : list<astropy.table.Table>
        List of PSF catalogues
    detections_catalogues : astropy.table.Table
        Detections catalogue, provided by MER
    
    """
   
    def __init__(self, exposures, stacked_image, detections_catalogue):
        """
        Parameters
        ----------
        exposures : list<SHEImage>
            List of SHEImage objects representing the different exposures
        stacked_image : SHEImage
            The stacked image
        detections_catalogue : astropy.table.Table
            Detections catalogue, provided by MER
          
        """
               
        self.exposures = exposures
        self.stacked_image = stacked_image
        self.detections_catalogue = detections_catalogue
        
        return
    
    @classmethod
    def _read_extension(cls, product_filename, tags=None, workdir=".", dtype=None):
        
        product = read_xml_product(os.path.join(workdir, product_filename))
        
        # Check it's the right type if necessary
        if dtype is not None:
            if not isinstance(product, dtype):
                raise ValueError("Data image product from " + product_filename + " is invalid type.")
            
        qualified_filename = os.path.join(workdir, product.get_filename())
        hdulist = fits.open(
            qualified_filename, mode="denywrite", memmap=True)
        
        header = hdulist[1].header
        
        if tags is None:
            data = hdulist[1].data
        else:
            data = []
            for tag in tags:
                extension = find_extension(hdulist, tag)
                data.append(hdulist[extension].data)
        
        return header, data

    @classmethod
    def read(cls,
             exposure_listfile_filename,
             bkg_listfile_filename,
             seg_listfile_filename,
             stacked_image_product_filename,
             stacked_bkg_product_filename,
             stacked_seg_product_filename,
             psf_listfile_filename,
             detections_product_filename,
             workdir = ".",
             **kwargs):
        """Reads a SHEFrameStack from relevant data products.
        
        
        Parameters
        ----------
        exposure_listfile_filename : str
            Filename of the listfile pointing to the exposure image data products
        bkg_listfile_filename : str
            Filename of the listfile pointing to the exposure background data products
        seg_listfile_filename : str
            Filename of the listfile pointing to the exposure segmentation map data products
        stacked_image_product_filename :frame_prod str
            Filename of the stacked image data product
        stacked_bkg_product_filename : str
            Filename of the stacked background data product
        stacked_seg_product_filename : str
            Filename of the stacked segmentation map data product
        psf_listfile_filename : str
            Filename of the listfile pointing to the psf data products
        detections_product_filename : str
            Filename of the detections catalog data product
        workdir : str
            Work directory
            
        Any kwargs are passed to the reading of the fits objects
        """
        
        # Load in the exposures as SHEFrames first
        exposures = []
        
        exposure_filenames = read_listfile(os.path.join(workdir,exposure_listfile_filename))
        bkg_filenames = read_listfile(os.path.join(workdir,bkg_listfile_filename))
        seg_filenames = read_listfile(os.path.join(workdir,seg_listfile_filename))
        psf_filenames = read_listfile(os.path.join(workdir,psf_listfile_filename))
        
        for exposure_i in range(len(exposure_filenames)):
            
            qualified_exposure_filename = os.path.join(workdir,exposure_filenames[exposure_i])
            qualified_bkg_filename = os.path.join(workdir,bkg_filenames[exposure_i])
            qualified_seg_filename = os.path.join(workdir,seg_filenames[exposure_i])
            qualified_psf_filename = os.path.join(workdir,psf_filenames[exposure_i])
            
            exposure = SHEFrame.read(frame_product_filename = qualified_exposure_filename,
                                     bkg_product_filename = qualified_bkg_filename,
                                     seg_product_filename = qualified_seg_filename,
                                     psf_product_filename = qualified_psf_filename,
                                     workdir=workdir)
    
            exposures.append(exposure)
            
        # Load in the stacked products now
        
        # Get the stacked image
        (stacked_image_header,
         stacked_data) = cls.read_extension(stacked_image_product_filename,
                                            tags = (mv.sci_tag, mv.noisemap_tag, mv.mask_tag),
                                            workdir = workdir,
                                            dtype = products.stacked_frame.DpdSheStackedFrameProduct)
         
        stacked_image_data = stacked_data[0]
        stacked_rms_data = stacked_data[1]
        stacked_mask_data = stacked_data[2]
        
        # Get the background image
        _, stacked_bkg_data = cls.read_extension(stacked_bkg_product_filename,
                                                 workdir = workdir,
                                                 dtype = products.stacked_frame.DpdSheStackedFrameProduct)
        
        # Get the segmentation image
        _, stacked_seg_data = cls.read_extension(stacked_seg_product_filename,
                                                 workdir = workdir,
                                                 dtype = products.stacked_frame.DpdSheStackedFrameProduct)
        
        # Construct a SHEImage object for the stacked image
        stacked_image = SHEImage( data = stacked_image_data,
                                  mask = stacked_rms_data,
                                  noisemap = stacked_mask_data,
                                  background_map = stacked_bkg_data,
                                  segmentation_map = stacked_seg_data,
                                  header = stacked_image_header,
                                  wcs = WCS( stacked_image_header ) )
        
        # Get the detections catalogue
        detections_product = read_xml_product( os.path.join( workdir, detections_product_filename ) )
        if not isinstance( detections_product, products.detections.DpdSheDetectionsProduct ):
            raise ValueError( "Detections product from " +
                              detections_product_filename + " is invalid type." )
            
        detections_catalogue = Table.read( os.path.join( workdir, detections_product.get_filename() ) )
        if not is_in_format(detections_catalogue, detf):
            raise ValueError( "Detections table from " +
                              detections_product.get_filename() + " is invalid type." )
        
        # Construct and return a SHEFrameStack object
        return SHEFrameStack( exposures = exposures,
                              stacked_image = stacked_image,
                              detections_catalogue = detections_catalogue)

    