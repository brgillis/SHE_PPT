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

import numpy as np
import astropy.io.fits # Avoid non-trivial "from" imports (as explicit is better than implicit)

import logging
logger = logging.getLogger(__name__)


class SHEImage(object): # We need new-style classes for properties, hence inherit from object
    """Structure to hold an image together with a mask and a noisemap.
    
    The structure can be written into a FITS file, and stamps can be extracted.
    The properties data, mask, and noisemap can be accessed directly.
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
        """A short string with useful information"""
        return "SHEImage{}".format(self.data.shape)
   
   
    
    def write_to_fits(self, filepath):
        """Writes the image to disk, in form of a FITS cube
        
        All the attributes of this image object are saved into the FITS file.
        
        Args:
            filepath: where the FITS file should be written
        """
        pass
    
        logger.info("Wrote {} to the FITS file {}".format(str(self), filepath))
 
      
    def extract_stamp(self, x, y, stamp_size):
        """Extracts a square stamp and returns it as a new instance (using views of numpy arrays, i.e., without making a copy)
      
        Args:
            x: x pixel coordinate on which to center the stamp. Will be rounded to the closest int.
            y: idem for y.
            stamp_size: width and height of the stamp, in pixels.
        """
        pass
        
    
    @classmethod
    def read_from_fits(cls, filepath):
        """Reads an image from a file written by write_to_fits(), and returns it as a SHEImage object.
      
        Args:
            filepath: from where the FITS image should be read
      
        """
        pass
 
 
 
 
