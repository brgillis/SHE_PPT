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



from future_builtins import *

import astropy.table

from SHE_PPT import detections_table_format
from SHE_PPT import psf_table_format
from SHE_PPT import table_utility
from SHE_PPT.she_image import SHEImage


class SHEImageData(object): # We need new-style classes for properties, hence inherit from object
    """Structure to group a science image with a corresponding detection table and PSF image
    
    Attributes
    ----------
    science_image : SHEImage
        The science exposure or image
    detections_table : astropy Table
        A table of sources detected in the science image
    bpsf_image : SHEImage
        An image containing PSF stamps for the bulge-components of galaxies.
    dpsf_image : SHEImage
        Idem for the disk-components.
    psf_table : astropy Table
        A table of PSF locations for sources detected in the science image
    """
   
    def __init__(self, science_image, detections_table, bpsf_image, dpsf_image, psf_table):
        """
        
        """

        self.science_image = science_image
        self.detections_table = detections_table
        self.bpsf_image = bpsf_image
        self.dpsf_image = dpsf_image
        self.psf_table = psf_table

    @classmethod
    def read(cls, science_image_filepath, detections_table_filepath, bpsf_image_filepath, dpsf_image_filepath,
             psf_table_filepath=None, **kwargs) :
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
        bpsf_image = SHEImage.read_from_fits(bpsf_image_filepath)
        dpsf_image = SHEImage.read_from_fits(dpsf_image_filepath)
        
        # And reading the detections table
        detections_table = cls.read_table(detections_table_filepath, check_format="detections_table")
        if psf_table_filepath is not None:
            psf_table = cls.read_table(psf_table_filepath, check_format="psf_table")
        
        # Building the object
        sid = SHEImageData(science_image, detections_table, bpsf_image, dpsf_image, psf_table)
        return sid


    @classmethod
    def read_table(cls, filepath, table_ext=None, check_format=None):
        """Reads-in a detections table from a FITS file
       
        Parameters
        ----------
        table_ext : str or None
            Name of the HDU to read the table from. If None, the primary HDU is read.
        
        
        """
    
        if table_ext is None:
            new_table = astropy.table.Table.read(filepath)
        else:
            new_table = astropy.table.Table.read(filepath, hdu=table_ext)
        
        # We check its format
        if check_format is not None:
            if check_format is "detections_table":
                table_utility.is_in_format(new_table, detections_table_format.tf)
            if check_format is "psf_table":
                table_utility.is_in_format(new_table, psf_table_format.tf)
    
        return new_table
    


