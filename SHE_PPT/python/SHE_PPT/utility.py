""" @file utility.py

    Created 25 Aug, 2017

    Miscellaneous utility functions
"""

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

import codecs
import hashlib
from copy import deepcopy

from SHE_PPT.wcsutil import WCS

from SHE_PPT import detector as dtc
from SHE_PPT.logging import getLogger

logger = getLogger(__name__)

def hash_any(obj,format='hex',max_length=None):
    """
        @brief Hashes any immutable object into a hex string of a given length. Unlike hash(),
               will be consistent in Python 3.0.
               
        @param obj
        
        @param format <str> Either 'hex' for hexadecimal string or 'base64' for a base 64 string.
                            This implementation of base64 replaces / with . so it will be
                            filename safe.
        
        @param max_length <int> Maximum length of hex string to return
        
        @return hash <str>
    """
    
    full_hash = hashlib.sha256(repr(obj).encode()).hexdigest()
    
    if format=='base64':
        # Recode it into base 64. Note that this results in a stray newline character
        # at the end, so we remove that.
        full_hash = codecs.encode(codecs.decode(full_hash,'hex'),'base64')[:-1]
        
        # This also allows the / character which we can't use, so replace it with .
        # Also decode it into a standard string
        full_hash = full_hash.decode().replace("/",".")
    
    if max_length is None or len(full_hash)<max_length:
        return full_hash
    else:
        return full_hash[:max_length]
    
def find_extension(hdulist,extname):
    """
        @brief Find the index of the extension of a fits HDUList with the correct EXTNAME value.
    """
    for i, hdu in enumerate(hdulist):
        if not "EXTNAME" in hdu.header:
            continue
        if hdu.header["EXTNAME"]==extname:
            return i
    return None

def get_detector(obj):
    """
        Find the detector indices for a fits hdu or table.
    """
    
    if hasattr(obj,"header"):
        header = obj.header
    elif hasattr(obj,"meta"):
        header = obj.meta
    else:
        raise ValueError("Unable to determine detector - no 'header' or 'meta' attribute present.")
    
    extname = header["EXTNAME"]
    
    detector_x = int(extname[dtc.x_index])
    detector_y = int(extname[dtc.y_index])
    
    return detector_x, detector_y

def time_to_timestamp(t):
    """
        From a struct_time object (as from the time module), get a timestamp in the astro format.
    """
    
    timestamp = (str(t.tm_year) + str(t.tm_mon) + str(t.tm_mday) + "T" +
                 str(t.tm_hour) + str(t.tm_min) + str(t.tm_sec)+ ".0Z")
    
    return timestamp

def load_wcs(header):
    """Create an astropy.wcs.WCS object from a FITS header, catching and correcting errors
    due to VIS's incorrect header keywords.
    
    This will be deprecated in the future once VIS's headers are corrected, at which point
    it will log a warning when used.
    """
    
    logger.debug("Entering load_wcs")
    
    if header is None:
        wcs = None
    else:
        wcs = WCS(header)
    
    logger.debug("Exiting load_wcs")
            
    return wcs
