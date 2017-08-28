#  
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
#

""" 
File: she_image.py

Created on: Aug 17, 2017
""" 
from __future__ import division, print_function
from future_builtins import *

import os
import numpy as np
import astropy.io.fits # Avoid non-trivial "from" imports (as explicit is better than implicit)

import logging
logger = logging.getLogger(__name__)


class SHEImage(object): # We need new-style classes for properties, hence inherit from object
    """Structure to hold an image together with a mask and a noisemap.
    
    The structure can be written into a FITS file, and stamps can be extracted.
    The properties data, mask, and noisemap are meant to be accessed directly.
    """
   
    def __init__(self, data, mask=None, noisemap=None):
        """Initiator
      
        Args:
            data: a 2D numpy array, with indices [x,y], consistent with DS9 and SExtractor orientation conventions.
            mask: an array of the same shape as data. Leaving None creates an empty mask
            noisemap: an array of the same shape as data. Leaving None creates a noisemap of ones
      
        """
               
        self.data = data # Note the tests done in the setter method
        self.mask = mask # Note that we translate None in the setter method 
        self.noisemap = noisemap
        
        logger.debug("Created {}".format(str(self)))
    
    
    # We define properties of the SHEImage object, following
    # https://euclid.roe.ac.uk/projects/codeen-users/wiki/User_Cod_Std-pythonstandard-v1-0#PNAMA-020-m-Developer-SHOULD-use-properties-to-protect-the-service-from-the-implementation
    
    @property
    def data(self):
        """The image array"""
        return self._data
    @data.setter
    def data(self, data_array):
        assert(data_array.ndim is 2) # Should probably raise exceptions instead, but this is better than nothing
        self._data = data_array
    @data.deleter
    def data(self):
        del self._data
        
    
    @property
    def mask(self):
        """The pixel mask of the image"""
        return self._mask
    @mask.setter
    def mask(self, mask_array):
        if mask_array is None:
            # Then we create an empty mask (all False)
            self._mask = np.zeros(self._data.shape, dtype=bool)
        else:
            assert(mask_array.ndim is 2)
            assert(mask_array.shape == self._data.shape)
            self._mask = mask_array
    @mask.deleter
    def mask(self):
        del self._mask
        
   
    @property
    def noisemap(self):
        """A noisemap of the image"""
        return self._noisemap
    @noisemap.setter
    def noisemap(self, noisemap_array):
        if noisemap_array is None:
            # Then we create a zero noisemap
            self._noisemap = np.ones(self._data.shape, dtype=float)
        else:
            assert(noisemap_array.ndim is 2)
            assert(noisemap_array.shape == self._data.shape)
            self._noisemap = noisemap_array
    @noisemap.deleter
    def noisemap(self):
        del self._noisemap
    
        
    def __str__(self):
        """A short string with size information and the percentage of masked pixels"""
        return "SHEImage({}x{}, {}%)".format(
            self.data.shape[0],
            self.data.shape[1], 
            100.0*float(np.sum(self.mask))/float(np.size(self.data))
        )
   
   
    
    def write_to_fits(self, filepath, clobber=False, **kwargs):
        """Writes the image to disk, in form of a multi-extension FITS cube.
        
        The data is written in the primary HDU, the mask in the extension 'MASK' and the noisemap in the extensions 'NOISEMAP'. 
        All the attributes of this image object are (should be ?) saved into the FITS file.
        
        Args:
            filepath: where the FITS file should be written
            clobber: if True, overwrites any existing file.
        """
           
        # Note that we transpose the numpy arrays, so to have the same pixel convention as DS9 and SExtractor.
        datahdu = astropy.io.fits.PrimaryHDU(self.data.transpose())
        maskhdu = astropy.io.fits.ImageHDU(data=self.mask.transpose().astype(np.uint8), name="MASK")
        noisemaphdu = astropy.io.fits.ImageHDU(data=self.noisemap.transpose(), name="NOISEMAP")
        
        hdulist = astropy.io.fits.HDUList([datahdu, maskhdu, noisemaphdu])
        
        if clobber is True and os.path.exists(filepath):
            logger.info("The output file exists and will get overwritten")
            
        hdulist.writeto(filepath, clobber=clobber)
        # Note that clobber is called overwrite in the latest astropy, but backwards compatible.
    
        logger.info("Wrote {} to the FITS file '{}'".format(str(self), filepath))
 
     
    @classmethod
    def read_from_fits(cls, filepath, maskext='MASK', noisemapext='NOISEMAP'):
        """Reads an image from a FITS file, such as written by write_to_fits(), and returns it as a SHEImage object.
        
        This function can be used both to read previously saved SHEImage objects, and to import other FITS images.
        The latter may have only one extension (in which case only the data is read, and mask and noisemap get created),
        or different extension names (to be specified using the keyword arguments).
        Note that the function "tranposes" all the arrays read from FITS, so that the properties of SHEImage can be
        indexed with [x,y] using the same convention as DS9 and SExtractor.
      
        Args:
            filepath: path to the FITS file to be read
            maskext: name of the extension containing the mask. Set it to None to not read any mask.
            noisemapext: idem, for the noisemap
      
        """
        
        hdulist = astropy.io.fits.open(filepath)  # open a FITS file
        nhdu = len(hdulist)
        
        logger.info("Reading file '{}', with {} extensions...".format(filepath, nhdu))
        
        # Reading the primary extension
        data_array = hdulist[0].data.transpose()
        if not data_array.ndim == 2: raise ValueError("Primary HDU must contain a 2D image")
        
        # Reading the mask
        mask_array = None
        if maskext is not None: 
            try:
                mask_array = hdulist[maskext].data.astype(bool).transpose()
            except KeyError:
                logger.warning("No extension '{}' found, setting mask to None!".format(maskext))
            
        # And the noisemap
        noisemap_array = None
        if noisemapext is not None:
            try:    
                noisemap_array = hdulist[noisemapext].data.transpose()
            except KeyError:
                logger.warning("No extension '{}' found, setting noisemap to None!".format(noisemapext))
            
        # Building and returning the new object    
        newimg = SHEImage(data=data_array, mask=mask_array, noisemap=noisemap_array)
        logger.info("Read {} from the file '{}'".format(str(newimg), filepath))
        return newimg
 
      
    def extract_stamp(self, x, y, stamp_size):
        """Extracts a square stamp and returns it as a new instance (using views of numpy arrays, i.e., without making a copy)
      
        Args:
            x: x pixel coordinate on which to center the stamp. Will be rounded to the closest int.
            y: idem for y.
            stamp_size: width and height of the stamp, in pixels.
        """
        pass
        
    

 
 
