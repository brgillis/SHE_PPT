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

__updated__ = "2021-04-22"

from enum import Enum
import os
import re

from EL_PythonUtils.utilities import (hash_any as EL_hash_any,
                                      run_only_once as EL_run_only_once,
                                      time_to_timestamp as EL_time_to_timestamp,
                                      get_arguments_string as EL_get_arguments_string)

from . import detector as dtc
from .logging import getLogger

logger = getLogger(__name__)

# Wrappers to warn functions which have moved to EL_PythonUtils


@EL_run_only_once
def warn_hash_any_deprecated():
    logger.warning("SHE_PPT.utility.hash_any has been moved to EL_PythonUtils.utilities.hash_any. " +
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def hash_any(*args, **kwargs):
    warn_hash_any_deprecated()
    return EL_hash_any(*args, **kwargs)


@EL_run_only_once
def warn_time_to_timestamp_deprecated():
    logger.warning("SHE_PPT.utility.time_to_timestamp has been moved to EL_PythonUtils.utilities.time_to_timestamp. " +
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def time_to_timestamp(*args, **kwargs):
    warn_time_to_timestamp_deprecated()
    return EL_time_to_timestamp(*args, **kwargs)


@EL_run_only_once
def warn_get_arguments_string_deprecated():
    logger.warning("SHE_PPT.utility.get_arguments_string has been moved to EL_PythonUtils.utilities.get_arguments_string. " +
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def get_arguments_string(*args, **kwargs):
    warn_get_arguments_string_deprecated()
    return EL_get_arguments_string(*args, **kwargs)


@EL_run_only_once
def warn_run_only_once_deprecated():
    logger.warning("SHE_PPT.utility.run_only_once has been moved to EL_PythonUtils.utilities.run_only_once. " +
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def run_only_once(*args, **kwargs):
    warn_run_only_once_deprecated()
    return EL_run_only_once(*args, **kwargs)


def get_attr_with_index(obj, attr):
    # Check for an index at the end of attr, using a regex which matches anything, followed by [, followed by a positive integer,
    # followed by ], followed by the end of the string. Matching groups are 1. the attribute, and 2. the index
    regex_match = re.match(r"(.*)\[([0-9]+)\]\Z", attr)

    if not regex_match:
        return getattr(obj, attr)
    else:
        # Get the attribute (matching group 1), indexed by the index (matching group 2)
        return getattr(obj, regex_match.group(1))[int(regex_match.group(2))]


def get_nested_attr(obj, attr):
    if not "." in attr:
        return get_attr_with_index(obj, attr)
    else:
        head, tail = attr.split('.', 1)
        return get_nested_attr(get_attr_with_index(obj, head), tail)


def set_index_zero_attr(obj, attr, val):
    if not "[0]" in attr:
        setattr(obj, attr, val)
    elif attr[-3:] == "[0]":
        getattr(obj, attr[:-3])[0] = val
    else:
        raise ValueError("Invalid format of attribute passed to get_attr_with_index: " + str(attr))
    return


def set_nested_attr(obj, attr, val):
    if not "." in attr:
        set_index_zero_attr(obj, attr, val)
    else:
        head, tail = attr.split('.', 1)
        set_nested_attr(get_attr_with_index(obj, head), tail, val)
    return


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


def find_extension(hdulist, extname=None, ccdid=None):
    """Find the index of the extension of a fits HDUList with the correct EXTNAME or CCDID value.
    """
    if extname is not None:
        for i, hdu in enumerate(hdulist):
            if not "EXTNAME" in hdu.header:
                continue
            if hdu.header["EXTNAME"] == extname:
                return i
        return None
    elif ccdid is not None:
        for i, hdu in enumerate(hdulist):
            if not "CCDID" in hdu.header:
                continue
            if hdu.header["CCDID"] == ccdid:
                return i
        return None
    else:
        raise ValueError("Either extname or ccdid must be supplied.")


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


def is_any_type_of_none(value):
    """Quick function to check if a value (which might be a string) is None or empty
    """
    return value in (None, "None", "", "data/None", "data/")


class AllowedEnum(Enum):

    @classmethod
    def is_allowed_value(cls, value):
        return value in [item.value for item in cls]
