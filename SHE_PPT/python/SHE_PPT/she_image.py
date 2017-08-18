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

import numpy as np
import astropy.io.fits # Avoid non-trivial "from" imports (as explicit is better than implicit)

import logging
logger = logging.getLogger(__name__)


class SHEImage:
   """Structure to hold an image together with a mask (and maybe a noisemap ?)
   
   """
   
   def __init__(self, data_array=None, mask_array=None, filepath=None):
      """
      
      Todo: later, use property decorator as recommended for EC code
      """
      self.data_array = data_array
      self.mask_array = mask_array
   
    
   def write_to_fits(self, filepath):
      """Writes the image to disk, in form of a FITS cube
      
         Args:
            filepath: where it should be written
      """
      pass
 
      
   def extract_stamp(self, x, y, stamp_size):
      """Extracts a square stamp and returns it as a new instance.
      
         Args:
            x: x pixel coordinate on which to center the stamp. Will be rounded to the closest int.
            y: idem for y.
            stamp_size: width and height of the stamp, in pixels.
      """
      pass
        
 
 
   def read_from_fits(filepath):
       """Reads an image from a file written by write_to_fits(), and returns it as a SHEImage object.
       
       """
 
 
 
