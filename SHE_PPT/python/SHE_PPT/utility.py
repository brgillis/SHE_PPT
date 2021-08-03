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

__updated__ = "2021-08-03"

from enum import Enum
import os
import re
from typing import Any, List, Optional, Tuple, Union

from EL_PythonUtils.utilities import (hash_any as EL_hash_any,
                                      run_only_once as EL_run_only_once,
                                      time_to_timestamp as EL_time_to_timestamp,
                                      get_arguments_string as EL_get_arguments_string)
from astropy.io.fits import TableHDU, HDUList
from astropy.table import Table

from . import detector as dtc
from .logging import getLogger


logger = getLogger(__name__)

# Wrappers to warn functions which have moved to EL_PythonUtils


@EL_run_only_once
def warn_hash_any_deprecated() -> None:
    logger.warning("SHE_PPT.utility.hash_any has been moved to EL_PythonUtils.utilities.hash_any. "
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def hash_any(*args, **kwargs) -> str:
    warn_hash_any_deprecated()
    return EL_hash_any(*args, **kwargs)


@EL_run_only_once
def warn_time_to_timestamp_deprecated() -> None:
    logger.warning("SHE_PPT.utility.time_to_timestamp has been moved to EL_PythonUtils.utilities.time_to_timestamp. "
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def time_to_timestamp(*args, **kwargs) -> str:
    warn_time_to_timestamp_deprecated()
    return EL_time_to_timestamp(*args, **kwargs)


@EL_run_only_once
def warn_get_arguments_string_deprecated() -> None:
    logger.warning("SHE_PPT.utility.get_arguments_string has been moved to EL_PythonUtils.utilities.get_arguments_string. "
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def get_arguments_string(*args, **kwargs) -> str:
    warn_get_arguments_string_deprecated()
    return EL_get_arguments_string(*args, **kwargs)


@EL_run_only_once
def warn_run_only_once_deprecated() -> None:
    logger.warning("SHE_PPT.utility.run_only_once has been moved to EL_PythonUtils.utilities.run_only_once. "
                   "Please update to use that, as this wrapper will be deprecated in a future version.")


def run_only_once(*args, **kwargs) -> Any:
    warn_run_only_once_deprecated()
    return EL_run_only_once(*args, **kwargs)


def get_attr_with_index(obj: Any, attr: Any) -> Any:
    # Check for an index at the end of attr, using a regex which matches anything, followed by [,
    # followed by a positive integer, followed by ], followed by the end of the string.
    # Matching groups are 1. the attribute, and 2. the index
    regex_match = re.match(r"(.*)\[([0-9]+)\]\Z", attr)

    if not regex_match:
        return getattr(obj, attr)
    # Get the attribute (matching group 1), indexed by the index (matching group 2)
    return getattr(obj, regex_match.group(1))[int(regex_match.group(2))]


def get_nested_attr(obj: Any, attr: Any) -> Any:
    if not "." in attr:
        return get_attr_with_index(obj, attr)
    head, tail = attr.split('.', 1)
    return get_nested_attr(get_attr_with_index(obj, head), tail)


def set_index_zero_attr(obj: Any, attr: Any, val: Any) -> None:
    if not "[0]" in attr:
        setattr(obj, attr, val)
    elif attr[-3:] == "[0]":
        getattr(obj, attr[:-3])[0] = val
    else:
        raise ValueError("Invalid format of attribute passed to get_attr_with_index: " + str(attr))


def set_nested_attr(obj: Any, attr: Any, val: Any):
    if not "." in attr:
        set_index_zero_attr(obj, attr, val)
    else:
        head, tail = attr.split('.', 1)
        set_nested_attr(get_attr_with_index(obj, head), tail, val)


def get_release_from_version(version: str) -> str:
    """Gets a 'release' format string ('XX.XX' where X is 0-9) from a 'version' format string ('X.X(.Y)',
       where each X is 0-99, and Y is any integer).
    """

    period_split_version = version.split('.')

    # Cast parts of the version string to int to check validity
    major_version = int(period_split_version[0])
    minor_version = int(period_split_version[1])

    if major_version < 0 or major_version > 99 or minor_version < 0 or minor_version > 99:
        raise ValueError("version (%s) is in incorrect format. Format must be 'X.X.X', where each X is "
                         "0-99." % version)

    # Ensure the string is two characters long for both the major and minor version
    major_version_string = str(major_version) if major_version > 9 else "0" + str(major_version)
    minor_version_string = str(minor_version) if minor_version > 9 else "0" + str(minor_version)

    return major_version_string + "." + minor_version_string


def find_extension(hdulist: HDUList,
                   extname: Optional[str] = None,
                   ccdid: Optional[str] = None):
    """Find the index of the extension of a fits HDUList with the correct EXTNAME or CCDID value.
    """
    if extname is not None:
        for i, hdu in enumerate(hdulist):
            if not "EXTNAME" in hdu.header:
                continue
            if hdu.header["EXTNAME"] == extname:
                return i
        return None
    if ccdid is not None:
        for i, hdu in enumerate(hdulist):
            if not "CCDID" in hdu.header:
                continue
            if hdu.header["CCDID"] == ccdid:
                return i
        return None
    raise ValueError("Either extname or ccdid must be supplied.")


def get_detector(obj: Union[TableHDU, Table]) -> Tuple[int, int]:
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


def get_all_files(directory_name: str) -> List[str]:
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


def process_directory(directory_name: str) -> Tuple[List[str], List[str]]:
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


def is_any_type_of_none(value: Any) -> bool:
    """Quick function to check if a value (which might be a string) is None or empty
    """
    return value in (None, "None", "", "data/None", "data/")


class AllowedEnum(Enum):

    @classmethod
    def is_allowed_value(cls, value: str) -> bool:
        return value in [item.value for item in cls]

    @classmethod
    def find_lower_value(cls, lower_value: str) -> "Optional[AllowedEnum]":
        for item in cls:
            if item.value.lower() == lower_value:
                return item
        return None
