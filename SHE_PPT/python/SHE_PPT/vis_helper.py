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
File: python/SHE_PPT/vis_helper.py

Created on: 09/12/17

This module contains helper functions to read data (images and catalogs) into SHEStack objects

"""

from __future__ import division, print_function
from future_builtins import *



from SHE_PPT.she_image_data import SHEImageData
from SHE_PPT.she_image import SHEImage
from SHE_PPT import table_utility
from SHE_PPT import detections_table_format

import astropy.table

import os
import json

import logging
logger = logging.getLogger(__name__)


def read_vis_ccdids(filepath):
    """Retruns a list of CCD-ID codes (i.e., whatever comes before the ".SCI" in the EXTNAME cards) of a VIS FITS image
    
    Coding style is not very compact but we try to be safe and informative.
    
    Parameters
    ----------
    filepath : str
        Path to the FITS file to read
    
    Returns
    -------
    list of strings
        sorted list of the unique CCD-ID codes
    """

    logger.debug("Reading VIS FITS file '{}'...".format(filepath))    
    hdulist = astropy.io.fits.open(filepath)
    logger.debug("It contains {} HDUs.".format(len(hdulist)))
    
    # Let's not test things we don't really need to test.
    #(nchips, remainder) = divmod(len(hdulist), 3)
    #if remainder != 0:
    #    raise RuntimeError("Number of extensions in VIS file is not a multiple of 3: {}".format(str(extension_names)))
   
    ccdids = []
    for hdu in hdulist:
        
        if (len(hdu.name) < 5) or (hdu.name[-4] != "."):
            raise ValueError("EXTNAME '{}' seems not compatible with the VIS format".format(hdu.name))
        
        ccdid = hdu.name[0:-4]
        ccdids.append(ccdid)
        
    hdulist.close()
    ccdids = sorted(list(set(ccdids)))
    return ccdids



def read_chip_from_vis_fits(filepath, ccdid):
    """Convenience function to read-in a specific chip (i.e., CCD) of a VIS-structured image into a SHEImage object
     
    The function groups the corresponding SCI, FLG, and RMS extensions as well as the related SCI header into one object.
    Note that VIS-files can be huge (real ones have 108 extensions), not all extensions can be read into memory at once.
    
    Parameters
    ----------
    filepath : str
        Path to the FITS file to read
    ccdid : str
        The CCD-ID code, i.e. whatever comes before ".SCI" in the EXTNAME header card
        
    Returns
    -------
    SHEImage
        A SHEImage
    
    """
    
    data_ext = str(ccdid) + ".SCI"
    mask_ext = str(ccdid) + ".FLG"
    noisemap_ext = str(ccdid) + ".RMS"
    
    new_image = SHEImage.read_from_fits(filepath,
                            data_ext=data_ext, mask_ext=mask_ext, noisemap_ext=noisemap_ext,
                            mask_filepath=None, noisemap_filepath=None)
    
    return new_image
    
 
    
    
    
    
def read_detections_table(filepath):
    """Reads-in a detection table from a FITS file"""
    
    new_table = astropy.table.Table.read(filepath)
    # We check its format
    table_utility.is_in_format(new_table, detection_table_format.tf)
    
    return new_table
    
    


def read_shestack_from_json(filepath, ccdid):
    """
    
    """
    

    
    
    
    
#     
# 
#     logger.info("Reading VIS FITS file '{}'...".format(filepath))
#     
#     hdulist = astropy.io.fits.open(filepath, uint=True)
#     extension_names = [hdu.name for hdu in hdulist]
#     nhdu = len(hdulist)
#     (nframes, remainder) = divmod(nhdu, 3)
#     if remainder != 0:
#         raise RuntimeError("Number of extensions in VIS file is not a multiple of 3: {}".format(str(extension_names)))
#     
#     output_list = []
#     for frame_index in range(nframes):
#         
#         # Getting all the data
#         data = hdulist["{}.SCI".format(frame_index)].data.transpose()
#         header = hdulist["{}.SCI".format(frame_index)].header
#         mask = hdulist["{}.FLG".format(frame_index)].data.transpose().astype(np.uint16)
#         noisemap = hdulist["{}.RMS".format(frame_index)].data.transpose()
#         for keyword in ["SIMPLE", "BITPIX", "NAXIS", "NAXIS1", "NAXIS2", "EXTEND", "XTENSION"]:
#             if keyword in header:
#                 header.remove(keyword)
#             
#         # Building the new object    
#         newimg = SHEImage(data=data, mask=mask, noisemap=noisemap, header=header)
#         output_list.append(newimg)
#      
#     assert len(output_list) == nframes
#     hdulist.close()
#     return output_list
# 
#      
#     
# def read_vis(filepath):
#     """Reads data from VIS output (under construction, to be defined!)
#     
#     """
#     
#     import json
# 
#     with open(filepath) as data_file:    
#         data = json.load(data_file)
#     
#     exppaths = data[0]
#     dalpaths = data[1]
#     dtcpaths = data[2]
#     psfpaths = data[3]
#     
#     logger.info("VIS list file contains {} EXP, {} DAL, {} DTC, and {} PSF paths".format(
#         len(exppaths), len(dalpaths), len(dtcpaths), len(psfpaths)))
#     
#     absdir = os.path.split(filepath)[0]
#     logger.debug("VIS data directory is '{}'".format(absdir))
#     
#     exposures = []
#     for (exp, dal, dtc, psf) in zip(exppaths, dalpaths, dtcpaths, psfpaths):
#         
#         science_image = SHEImage.read_from_fits(os.path.join(absdir, exp), mask_ext=None, noisemap_ext=None)
#         psf_image = SHEImage.read_from_fits(os.path.join(absdir, psf), mask_ext=None, noisemap_ext=None)
#          
#         # And reading the detections table
#         detections_table = astropy.table.Table.read(os.path.join(absdir, dtc))
#     
#         # Building the object
#         sid = SHEImageData(science_image, detections_table, psf_image)
#         exposures.append(sid)
#     
#     return SHEStack(exposures)
# 
#  
