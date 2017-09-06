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
File: python/SHE_PPT/she_stack.py

Created on: 09/01/17
Author: user
"""

from __future__ import division, print_function
from future_builtins import *

from SHE_PPT.she_image_data import SHEImageData

import logging
logger = logging.getLogger(__name__)



class SHEStack(object): # We need new-style classes for properties, hence inherit from object
    """Structure containing a list of SHEImageData objects, serving as input to the estimate_shear() methods
    
    Attributes
    ----------
    exposures : list
        List of SHEImageData objects representing the different exposures
    
    
    We might want to add an attribute 'stack' later.
    
    """
   
    def __init__(self, exposures):
        """
        Parameters
        ----------
        exposures : list
            a list of SHEImageData objects representing the different exposures
          
        """
               
        self.exposures = exposures
    

    @classmethod
    def read(cls, filepaths_list, **kwargs):
        """Reads a SHEStack from disk
        
        This function successively calls SHEImageData.read() on contents of filepaths_list.
        
        
        Parameters
        ----------
        filepaths_list : list
            a list of lists of filepaths to the FITS files containing SHEImage objects and astropy Tables.
            The structure is the following::
            
                filepath_list = [
                    ["exp1.fits", "detections1.fits", "psf1.fits"],
                    ["exp2.fits", "detections2.fits", "psf2.fits"],
                    ...
                ]
            
        Any kwargs are passed to the reading of the SHEImageData
        """
        
        exposures = []
        for filepaths in filepaths_list:
            exposures.append(SHEImageData.read(*filepaths))
        
        return SHEStack(exposures)




