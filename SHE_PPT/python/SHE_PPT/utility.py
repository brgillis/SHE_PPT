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

__updated__ = "2020-06-30"

import codecs
import hashlib
import os

from astropy.wcs import WCS

from SHE_PPT import detector as dtc
from SHE_PPT.logging import getLogger

logger = getLogger(__name__)


def get_index_zero_attr(obj, attr):
    if not "[0]" in attr:
        return getattr(obj, attr)
    elif attr[-3:] == "[0]":
        return getattr(obj, attr[:-3])[0]
    else:
        raise ValueError("Invalid format of attribute passed to get_index_zero_attr: " + str(attr))


def get_nested_attr(obj, attr):
    if not "." in attr:
        return get_index_zero_attr(obj, attr)
    else:
        head, tail = attr.split('.', 1)
        return get_nested_attr(get_index_zero_attr(obj, head), tail)


def set_index_zero_attr(obj, attr, val):
    if not "[0]" in attr:
        setattr(obj, attr, val)
    elif attr[-3:] == "[0]":
        getattr(obj, attr[:-3])[0] = val
    else:
        raise ValueError("Invalid format of attribute passed to get_index_zero_attr: " + str(attr))
    return


def set_nested_attr(obj, attr, val):
    if not "." in attr:
        set_index_zero_attr(obj, attr, val)
    else:
        head, tail = attr.split('.', 1)
        set_nested_attr(get_index_zero_attr(obj, head), tail, val)
    return


def hash_any(obj, format='hex', max_length=None):
    """Hashes any immutable object into a hex string of a given length. Unlike hash(), will be consistent in Python
    3.0.

    Parameters
    ----------
    obj : Any immutable
        The object to be hashed
    format : str
        'hex' for hexadecimal string, 'base64' for a base 64 string (This implementation of base64 replaces '/' with
        '.' so it will be filename safe), 'int'/'uint' for (un)signed integer, '(u)int8', '(u)int16', etc. for
        (un)signed integer of a given maximum size,
    max_length : int
        If format is 'hex' or 'base64', this limits the maximum length of the string to return

    Return
    ------
    hash : str (if format is 'hex' or 'base64') or desired integer type
    """

    full_hash = hashlib.sha256(repr(obj).encode()).hexdigest()

    if format == 'hex':
        pass  # Hex is default behavior
    elif format == 'base64':
        # Recode it into base 64. Note that this results in a stray newline character
        # at the end, so we remove that.
        full_hash = codecs.encode(
            codecs.decode(full_hash, 'hex'), 'base64')[:-1]

        # This also allows the / character which we can't use, so replace it with .
        # Also decode it into a standard string
        full_hash = full_hash.decode().replace("/", ".")
    elif format[0:3] == 'int' or format[0:4] == 'uint':
        int_hash = int("0x" + full_hash, 0)
        if format == 'int' or format == 'uint':
            full_hash = int_hash
        else:
            if format[0] == 'i':
                start = 3
                signed = True
            else:
                start = 4
                signed = False

            # Get the power from the portion after the 'int' part
            power = int(format[start:])
            mod = 2 ** power
            full_hash = int_hash % mod

            # If signed, subtract half the modulus
            if signed:
                full_hash -= mod // 2
    else:
        raise ValueError("Unknown format: " + str(format))

    if not (format[0:3] == 'int' or format[0:4] == 'uint'):
        if max_length is None or len(full_hash) < max_length:
            pass
        else:
            full_hash = full_hash[:max_length]
    return full_hash


def get_release_from_version(version):
    """Gets a 'release' format string ('XX.XX' where X is 0-9) from a 'version' format string ('X.X(.Y)', where each X is
       0-99, and Y is any integer).
    """

    period_split_version = version.split('.')

    # Cast parts of the version string to int to check validity
    major_version = int(period_split_version[0])
    minor_version = int(period_split_version[1])

    if major_version < 0 or major_version > 99 or minor_version < 0 or minor_version > 99:
        raise ValueError("version (" + version + ") is in incorrect format. Format must be 'X.X.X', where each X is " +
                         "0-99.")

    # Ensure the string is two characters long for both the major and minor version
    major_version_string = str(major_version) if major_version > 9 else "0" + str(major_version)
    minor_version_string = str(minor_version) if minor_version > 9 else "0" + str(minor_version)

    return major_version_string + "." + minor_version_string


def find_extension(hdulist, extname):
    """Find the index of the extension of a fits HDUList with the correct EXTNAME value.
    """
    for i, hdu in enumerate(hdulist):
        if not "EXTNAME" in hdu.header:
            continue
        if hdu.header["EXTNAME"] == extname:
            return i
    return None


def get_detector(obj):
    """Find the detector indices for a fits hdu or table.
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
    """From a datetime object, get a timestamp in the astro format.
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
            if 'TAN' in header['CTYPE1'] or 'TAN' in header['CTYPE2']:
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


def get_arguments_string(args, cmd=None, store_true=None, store_false=None):
    """Turns an args variable (as from parse_args) into a string that can be used for execution.

    Parameters
    ----------
    args : <object> Any object with attributes, as from parse_args
    cmd : <str> If not none, will be put at the beginning of the output string followed by a space

    Return
    ------
    String of all needed commands

    """

    # Set up defaults
    if store_true is None:
        store_true = []
    if store_false is None:
        store_false = []

    if cmd is not None:
        arg_string = cmd.strip() + " "
    else:
        arg_string = ""

    arglib = vars(args)

    # Loop over all arguments
    for arg in arglib:

        val = arglib[arg]

        # Skip if it's private or the value is None
        if arg[0] == "_" or val is None:
            continue

        # Properly handle bools for store_true/false cases
        if isinstance(val, bool):
            if arg in store_true:
                if val:
                    arg_string += "--" + arg.strip() + " "
            elif arg in store_false:
                if not val:
                    arg_string += "--" + arg.strip() + " "
            else:
                arg_string += "--" + arg.strip() + " " + str(val).strip() + " "
            continue

        # Add arg to arg string
        stripped_arg = arg.strip()

        if stripped_arg == "log_file":
            # Correct for Elements somehow switching log-file to log_file
            arg_string += "--" + "log-file" + " "
        elif stripped_arg == "log_level":
            # Correct for Elements somehow switching log-level to log_level
            arg_string += "--" + "log-level" + " "
        else:
            arg_string += "--" + stripped_arg + " "

        stripped_val = str(val).strip()

        # Properly handle lists of values
        if isinstance(val, list):
            for subval in val:
                # Put quotes around each subval if it includes a space
                stripped_subval = str(subval).strip()
                if " " in stripped_subval:
                    arg_string += '"' + stripped_subval + '" '
                else:
                    arg_string += stripped_subval + " "
        elif " " in stripped_val:
            # If there's a space in val and it's not a list, put quotes around it
            arg_string += '"' + stripped_val + '" '
        elif stripped_val == "":
            # If it's an empty string, output quotes instead of nothing
            arg_string += '"" '
        else:
            arg_string += stripped_val + " "

    # Clean trailing space
    arg_string = arg_string.strip()

    return arg_string


def run_only_once(function):
    """Decorator so that the function it decorates will only execute one time. Useful for logging warnings, when you
    only want to warn for something the first time.
    """

    # Define a wrapper function that only runs if it hasn't already
    def wrapper(*args, **kwargs):
        if not wrapper.already_run:
            wrapper.already_run = True
            return function(*args, **kwargs)
        else:
            return None

    # Set wrapper as not having already run
    wrapper.already_run = False

    return wrapper


def get_all_files(directory_name):
    """
    """
    full_file_list = []
    dir_list = [directory_name]
    is_complete = False
    while not is_complete:
        new_dir_list = []
        for dir_name in dir_list:
            file_list, sb_dir_list = process_directory(
                dir_name)
            full_file_list += [os.path.join(dir_name, fname)
                             for fname in file_list]
            if sb_dir_list:
                new_dir_list += [os.path.join(dir_name, sb_dir)
                    for sb_dir in sb_dir_list]
        dir_list = new_dir_list
        is_complete = len(dir_list) == 0

    return full_file_list


def process_directory(directory_name):
    """ Check for files, subdirectories
    
    """
    file_list = []
    subdir_list = []
    for file_name in os.listdir(directory_name):
        if os.path.isdir(os.path.join(directory_name, file_name)):
            subdir_list.append(file_name)
        elif not file_name.startswith('.'):
            file_list.append(file_name)
    return file_list, subdir_list
