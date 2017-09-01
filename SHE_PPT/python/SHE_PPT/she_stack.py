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


import logging
logger = logging.getLogger(__name__)



class SHEStack(object): # We need new-style classes for properties, hence inherit from object
    """Structure to group data images, PSF images, and detection tables of multiple exposures as input to estimate_shear()"""
   
    def __init__(self, data_images, psf_images, detection_tables):
        """Initiator
      
        Args:
            data_images: a list of SHEImage objects
            psf_images: a corresponding list of SHEImages containing PSFs
            detection_tables: a corresponding list of detection tables
      
        """
               
        self.data_images = data_images
        self.psf_images = psf_images
        self.detection_tables = detection_tables
    
