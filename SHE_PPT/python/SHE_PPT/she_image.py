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
    Note that the shape (and size) of data, mask and noisemap cannot be modified once the object exists, as such a
    change would probably not be wanted. If you really want to change the size of a SHEImage, make a new object.
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
        # We test the dimensionality
        if data_array.ndim is not 2:
            raise ValueError("Data array of a SHEImage must have 2 dimensions")
        # We test that the shape is not modified by the setter, if a shape already exists.
        try:
            existing_shape = self.shape
        except AttributeError:
            existing_shape = None
        if existing_shape:
            if data_array.shape != existing_shape:
                raise ValueError("Shape of a SHEImage can not be modified. Current is {}, new data is {}.".format(
                    existing_shape, data_array.shape
                    ))
        # And perform the attribution
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
            if mask_array.ndim is not 2:
                raise ValueError("The mask array must have 2 dimensions")
            if mask_array.shape != self._data.shape:
                raise ValueError("The mask array must have the same size as the data {}".format(self._data.shape))
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
            if noisemap_array.ndim is not 2:
                raise ValueError("The noisemap array must have 2 dimensions")
            if noisemap_array.shape != self._data.shape:
                raise ValueError("The noisemap array must have the same size as its data {}".format(self._data.shape))
            self._noisemap = noisemap_array
    @noisemap.deleter
    def noisemap(self):
        del self._noisemap
    

    @property
    def shape(self): # Just a shortcut, also to stress that all arrays (data, mask, noisemap) have the same shape.
        """The shape of the image, equivalent to self.data.shape"""
        return self.data.shape
        
    def __str__(self):
        """A short string with size information and the percentage of masked pixels"""
        return "SHEImage({}x{}, {}%)".format(
            self.shape[0],
            self.shape[1], 
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
        
        We might want to add further options in future, e.g. a way to read mask and noisemap from external files.
        
        Args:
            filepath: path to the FITS file to be read
            maskext: name of the extension containing the mask. Set it to None to not read any mask.
            noisemapext: idem, for the noisemap
      
        """
        
        hdulist = astropy.io.fits.open(filepath)  # open a FITS file
        nhdu = len(hdulist)
        
        logger.debug("Reading file '{}', with {} extensions...".format(filepath, nhdu))
        
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
 
      
    def extract_stamp(self, x, y, width, height=None):
        """Extracts a stamp and returns it as a new instance (using views of numpy arrays, i.e., without making a copy)
        
        The extracted stamp is centered on the given (x,y) coordinates and has shape (width, height).
        To define this center, two alternative conventions are implemented.
        
        The convention for the pixel-coordinates is the same as used by DS9 and SExtractor: the bottom-left pixel has
        coordinates (0.5, 0.5), i.e., it spreads from (0.0, 0.0) to (1.0,1.0). 
        
        For now, the function raises a ValueError if the stamp is not entirely within the image.
        We will change this in future, to extract on-edge stamps and reflect this by masking the non-existing pixels.
              
        Args:
            x: x pixel coordinate on which to center the stamp. Can be a float or an int.
            y: idem for y
            width: the width of the stamp to extract
            height: the height. If left to None, a square stamp (width x width) will get extracted.
            
        """
        
        # Should we extract a square stamp?
        if height is None:
            height = width
        
        # Checking stamp size
        width = int(round(width))
        height = int(round(height))
        if width < 1 or height < 1:
            raise ValueError("Stamp height and width must at least be 1")
        
        # The bottom-left pixel is centered on (0.5, 0.5)
        xmin = int(round(x - width/2.0))
        ymin = int(round(y - height/2.0))
        xmax = xmin + width
        ymax = ymin + height
        
        # We check that these bounds are fully within the image range
        if xmin < 0 or xmax > self.shape[0] or ymin < 0 or ymax > self.shape[1]:
            raise ValueError("Stamp [{}:{},{}:{}], is not within image shape {}".format(xmin, xmax, ymin, ymax, self.shape))
        
        logger.debug("Extracting stamp [{}:{},{}:{}] from image of shape {}".format(xmin, xmax, ymin, ymax, self.shape))
        
        newimg = SHEImage(
            data=self.data[xmin:xmax,ymin:ymax],
            mask=self.mask[xmin:xmax,ymin:ymax],
            noisemap=self.noisemap[xmin:xmax,ymin:ymax]
            )
        assert newimg.shape == (width, height)
        
        return newimg

 
