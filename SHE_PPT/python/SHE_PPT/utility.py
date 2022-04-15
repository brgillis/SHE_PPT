""" @file utility.py

    Created 25 Aug, 2017

    Miscellaneous utility functions
"""

__updated__ = "2021-08-30"

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

import os
import re
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Type, TypeVar, Union

import numpy as np
from astropy.io.fits import HDUList, TableHDU
from astropy.table import Table

from . import detector as dtc
from .logging import getLogger

logger = getLogger(__name__)


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


# Value testing functions


def is_any_type_of_none(value: Any) -> bool:
    """Quick function to check if a value (which might be a string) is None or empty
    """
    return value in (None, "None", "", "data/None", "data/")


def any_is_inf(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is inf.
    """
    return np.logical_or.reduce(np.isinf(l_x))


def any_is_nan(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is NaN.
    """
    return np.logical_or.reduce(np.isnan(l_x))


def any_is_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is masked. This can actually be done by a single function call with
        numpy, but this wrapper is presented here for consistency with Inf and NaN checks, so a user searching for a
        function to do this isn't left confused by its absence.
    """
    return np.ma.is_masked(l_x)


def is_inf_or_nan(x: Union[float, Sequence[float]]) -> bool:
    """ Checks if a value is inf or NaN.
    """
    return np.logical_or(np.isinf(x), np.isnan(x))


def any_is_inf_or_nan(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is inf or nan.
    """
    return np.logical_or.reduce(is_inf_or_nan(l_x))


def is_nan_or_masked(x: Union[float, Sequence[float]]) -> bool:
    """ Checks if a value is NaN or masked.
    """
    return np.logical_or(np.isnan(x), np.ma.is_masked(x))


def any_is_nan_or_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is NaN or masked.
    """
    return np.logical_or.reduce(is_nan_or_masked(l_x))


def is_inf_nan_or_masked(x: Union[float, Sequence[float]]) -> bool:
    """ Checks if a value is Inf, NaN, or masked.
    """
    return np.logical_or(np.isinf(x), is_nan_or_masked(x))


def any_is_inf_nan_or_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """ Checks if any value in a sequence of values is Inf, NaN or masked.
    """
    return np.logical_or.reduce(is_inf_nan_or_masked(l_x))


Number = TypeVar('Number', float, int)


def is_zero(x: Number):
    """ Checks if a value is zero - needed if a callable function is required to perform this test.
    """
    return x == 0


def any_is_zero(l_x: Sequence[Number]) -> bool:
    """ Checks if any value in a sequence of numbers is zero.
    """
    return (np.asarray(l_x) == 0).any()


def all_are_zero(l_x: Sequence[Number]) -> bool:
    """ Checks if all values in a sequence of numbers are zero.
    """
    return (np.asarray(l_x) == 0).all()


# List/join and other collection functions

T = TypeVar('T')
TK = TypeVar('TK')
TV = TypeVar('TV')


def default_value_if_none(x: Optional[T],
                          default_x: T) -> T:
    """ If input value is None, returns a provided default value, otherwise returns the input
        value.
    """
    if x is None:
        return default_x
    return x


def default_init_if_none(x: Optional[Any],
                         type: Type[T],
                         *args,
                         coerce: bool = False,
                         **kwargs) -> T:
    """ If input value is None, returns a default initialization of the provided type, otherwise returns the input
        value. Optionally tries to coerce to desired type.
    """
    if x is None:
        return type(*args, **kwargs)
    if coerce:
        return type(x)
    return x


def empty_list_if_none(l_x: Optional[Sequence[T]],
                       coerce: bool = False) -> List[T]:
    """ If input value is None, returns an empty list, otherwise returns the input value.
    """
    return default_init_if_none(l_x, list, coerce = coerce)


def empty_set_if_none(s_x: Optional[Union[Sequence[T], Set[T]]],
                      coerce: bool = False) -> Set[T]:
    """ If input value is None, returns an empty set, otherwise returns the input value.
    """
    return default_init_if_none(s_x, type = set, coerce = coerce)


def empty_dict_if_none(d_x: Optional[Dict[TK, TV]],
                       coerce: bool = False) -> Dict[TK, TV]:
    """ If input value is None, returns an empty dict, otherwise returns the input value.
    """
    return default_init_if_none(d_x, type = dict, coerce = coerce)


def coerce_to_list(a: Union[None, T, List[T]],
                   keep_none: bool = False) -> Union[List[T], None]:
    """ Coerces either None, a single item, or a list to a list of items.

        If keep_none is False, will convert None to an empty list.
        If keep_none is True, will return None if None is input.
    """
    if a is None:
        l_a = None if keep_none else []
    elif isinstance(a, str):
        # Special handling for strings, which are interable, but we don't want lists of their characters
        l_a = [a]
    else:
        # Check if it's iterable, and convert to list if so
        try:
            l_a = list(a)
        except TypeError:
            # Not iterable, so return as an element of a list
            l_a = [a]

    return l_a


def join_without_none(l_s: List[Optional[Any]], joiner: str = "-", default: Optional[str] = "") -> Optional[str]:
    """ Join a list of values into a single string, excepting any Nones.
    """

    # Get a list to join without any Nones
    l_s_no_none: List[str] = [str(s) for s in l_s if s is not None]

    # Return the default if the list is empty
    if len(l_s_no_none) == 0:
        return default

    # Otherwise, join the pieces
    return joiner.join(l_s_no_none)
