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





from SHE_PPT.she_image_data import SHEImageData
from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_stack import SHEStack

from SHE_PPT import table_utility
from SHE_PPT import detections_table_format

import astropy.table

import os
import json

from . import logging
logger = logging.getLogger(__name__)


def read_vis_ccdids(filepath):
    """Retruns a list of CCD-ID codes (i.e., whatever comes before the ".SCI" in the EXTNAME cards) of a VIS FITS image
    
    Todo: make this more general also for other (longer) ext_codes?
    
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



def read_chip_from_vis_fits(filepath, ccdid, ext_code=None):
    """Convenience function to read-in a specific chip (i.e., CCD) of a VIS-structured image into a SHEImage object
     
    The function groups the corresponding SCI, FLG, and RMS extensions as well as the related SCI header into one object.
    Note that VIS-files can be huge (real ones have 108 extensions), not all extensions can be read into memory at once.
    
    
    Parameters
    ----------
    filepath : str
        Path to the FITS file to read
    ccdid : str
        The CCD-ID code, i.e. whatever comes before ".SCI" in the EXTNAME header card
    ext_code : None or str
        When reading FITS files which mimic a VIS-like structure with several chips per file,
        but don't have SCI, FLG, and RMS extension, set this to the extension code (i.e., whatever follows the dot
        in the EXTNAME), for instance "BPSF", to read this instead of SCI, FLG, and RMS.
        EXTNAME format: ccdid + "." + ext_code
        
    Returns
    -------
    SHEImage
        A SHEImage
    
    """
    
    if ext_code is None:
        data_ext = str(ccdid) + ".SCI"
        mask_ext = str(ccdid) + ".FLG"
        noisemap_ext = str(ccdid) + ".RMS"
        segmentation_map_ext = None # Not provided by VIS, to be added later
    
    else:
        data_ext = str(ccdid) + "." + ext_code
        mask_ext = None
        noisemap_ext = None
        segmentation_map_ext = None
    
    new_image = SHEImage.read_from_fits(filepath,
                            data_ext=data_ext, mask_ext=mask_ext,
                            noisemap_ext=noisemap_ext, segmentation_map_ext=segmentation_map_ext,
                            mask_filepath=None, noisemap_filepath=None, segmentation_map_filepath=None)
    
    return new_image
    
    

def read_detections_table_for_vis_fits(filepath, ccdid):
    """Analogue of read_chip_from_vis_fits, but for detections tables as written by SHE_GST.
    
    """
    detection_table_ext = str(ccdid) + ".DTC"
    
    new_table = SHEImageData.read_table(filepath, table_ext=detection_table_ext, check_format="detections_table")
    
    return new_table



def read_shestack_from_gst_json(filepath, ccdid):
    """Convenience function to read a SHEStack object based on a VIS-like data structured generated by GST 
    
    The API of this will likely change in near future, this is just a start
    """
    
    logger.info("Reading SHEStack from list file '{}'...".format(filepath))
    with open(filepath) as data_file:    
        data = json.load(data_file)
     
    exppaths = data[0]
    dalpaths = data[1]
    dtcpaths = data[2]
    psfpaths = data[3]
     
    logger.info("List file contains {} EXP, {} DAL, {} DTC, and {} PSF paths".format(
        len(exppaths), len(dalpaths), len(dtcpaths), len(psfpaths)))
    
    assert len(exppaths) == len(dalpaths)
    assert len(exppaths) == len(dtcpaths)
    assert len(exppaths) == len(psfpaths)
    
    absdir = os.path.split(filepath)[0]
    logger.debug("VIS data directory is '{}'".format(absdir))
     
    exposures = []
    logger.info("Starting loop over exposures")
    for i, (exp, dal, dtc, psf) in enumerate(zip(exppaths, dalpaths, dtcpaths, psfpaths)):
        
        logger.info("Reading-in exposure {}/{}...".format(i+1, len(exppaths)))
        science_image = read_chip_from_vis_fits(os.path.join(absdir, exp), ccdid=ccdid)
        
        bpsf_image = read_chip_from_vis_fits(os.path.join(absdir, psf), ccdid=ccdid, ext_code="BPSF")
        dpsf_image = read_chip_from_vis_fits(os.path.join(absdir, psf), ccdid=ccdid, ext_code="DPSF")
        
        #SHEImage.read_from_fits(os.path.join(absdir, psf), mask_ext=None, noisemap_ext=None)
          
        # And reading the detections table
        detections_table = read_detections_table_for_vis_fits(os.path.join(absdir, dtc), ccdid=ccdid)
     
        # Building the object
        sid = SHEImageData(science_image, detections_table, bpsf_image, dpsf_image, None)
        exposures.append(sid)
    
    logger.info("Done with loop over exposures")
    return SHEStack(exposures)
    
    
    