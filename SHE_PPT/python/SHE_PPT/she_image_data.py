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
File: python/SHE_PPT/she_image_data.py

Created on: 09/06/17
"""

from __future__ import division, print_function
from future_builtins import *

from SHE_PPT.she_image import SHEImage
from astropy.table import Table

class SHEImageData(object): # We need new-style classes for properties, hence inherit from object
    """Structure to group a science image with a corresponding detection table and PSF image
    
    Attributes
    ----------
    science_image : SHEImage
        The science exposure or image
    detections_table : astropy Table
        A table of sources detected the science image
    psf_image : SHEImage
        An image containing PSF stamps
    """
   
    def __init__(self, science_image, detections_table, psf_image):
        """
        
        """

        self.science_image = science_image
        self.detections_table = detections_table
        self.psf_image = psf_image

    @classmethod
    def read(cls, science_image_filepath, detections_table_filepath, psf_image_filepath, **kwargs) :
        """Reads-in a SHEImageData from disk
        
        Parameters
        ----------
        science_image_filepath : str
            Filepath to a FITS file containing the science SHEImage
        detections_table_filepath : str
            Filepath to a FITS file containing the detections table
        psf_image_filepath : str
            Filepath to a FITS file containing the PSF SHEImage
        
        Any additional kwargs are passed to the reading of the science image
        
        Returns
        -------
        SHEImageData
            The new object, read from disk.
        
        """
        
        # Reading the SHEImages
        science_image = SHEImage.read_from_fits(science_image_filepath, **kwargs)
        psf_image = SHEImage.read_from_fits(psf_image_filepath)
        
        # And reading the detections table
        detections_table = Table.read(detections_table_filepath)
        
        # Building the object
        sid = SHEImageData(science_image, detections_table, psf_image)
        return sid


