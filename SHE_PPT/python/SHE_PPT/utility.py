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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import codecs
from copy import deepcopy
import hashlib

from astropy.wcs import WCS

from SHE_PPT import detector as dtc
from SHE_PPT.logging import getLogger


logger = getLogger(__name__)


def hash_any(obj, format='hex', max_length=None):
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

    if format == 'base64':
        # Recode it into base 64. Note that this results in a stray newline character
        # at the end, so we remove that.
        full_hash = codecs.encode(
            codecs.decode(full_hash, 'hex'), 'base64')[:-1]

        # This also allows the / character which we can't use, so replace it with .
        # Also decode it into a standard string
        full_hash = full_hash.decode().replace("/", ".")

    if max_length is None or len(full_hash) < max_length:
        return full_hash
    else:
        return full_hash[:max_length]


def find_extension(hdulist, extname):
    """
        @brief Find the index of the extension of a fits HDUList with the correct EXTNAME value.
    """
    for i, hdu in enumerate(hdulist):
        if not "EXTNAME" in hdu.header:
            continue
        if hdu.header["EXTNAME"] == extname:
            return i
    return None


def get_detector(obj):
    """
        Find the detector indices for a fits hdu or table.
    """

    if hasattr(obj, "header"):
        header = obj.header
    elif hasattr(obj, "meta"):
        header = obj.meta
    else:
        raise ValueError(
            "Unable to determine detector - no 'header' or 'meta' attribute present.")

    extname = header["EXTNAME"]

    detector_x = int(extname[dtc.x_index])
    detector_y = int(extname[dtc.y_index])

    return detector_x, detector_y


def time_to_timestamp(t):
    """
        From a datetime object, get a timestamp in the astro format.
    """

    timestamp = (str(t.year) + str(t.month) + str(t.day) + "T" +
                 str(t.hour) + str(t.minute) + str(t.second) + "." + str(t.microsecond // 100000) + "Z")

    return timestamp


def load_wcs(header, apply_sc3_fix=False):
    """Create an astropy.wcs.WCS object from a FITS header, catching and correcting errors
    due to VIS's incorrect header keywords.

    This will be deprecated in the future once VIS's headers are corrected, at which point
    it will log a warning when used.
    """

    logger.debug("Entering load_wcs")

    if header is None:
        wcs = None
    else:

        if apply_sc3_fix:
            # fix VIS bug in WCS (won't be needed in future releases)
            # uses TPV (Scamp like WCS) instead of TAN projection,
            # which would break the subsequent line
            # source: LensMC and https://euclid.roe.ac.uk/issues/7409
            if 'TAN' in header['CTYPE1'] or header['CTYPE2']:
                header['CTYPE1'] = 'RA---TPV'
                header['CTYPE2'] = 'DEC--TPV'
            if 'PC1_1' in header:
                header.remove('PC1_1')
            if 'PC1_2' in header:
                header.remove('PC1_2')
            if 'PC2_1' in header:
                header.remove('PC2_1')
            if 'PC2_2' in header:
                header.remove('PC2_2')
            if 'CDELT1' in header:
                header.remove('CDELT1')
            if 'CDELT2' in header:
                header.remove('CDELT2')

        wcs = WCS(header)

    logger.debug("Exiting load_wcs")

    return wcs

def get_arguments_string(args, cmd=None):
    """Turns an args variable (as from parse_args) into a string that can be used for execution.
    
    Parameters
    ----------
    args : <object> Any object with attributes, as from parse_args
    cmd : <str> If not none, will be put at the beginning of the output string followed by a space
    
    Return
    ------
    <str> String of all needed commands
    
    """

    if cmd is not None:
        arg_string = cmd.strip() + " "
    else:
        arg_string = ""
    
    arglib = vars(args)
    
    # Loop over all arguments
    for arg in arglib:
        
        # Skip if it's private
        if arg[0]=="_":
            continue
        
        # Add it to the arg_string
        arg_string += "--" + arg.strip() + " " + str(arglib[arg]).strip()
        
    # Clean trailing space
    arg_string = arg_string.strip()
    
    return arg_string
