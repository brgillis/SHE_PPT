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
from typing import Any, Dict, List, MutableSequence, Optional, Sequence, Set, Tuple, Type, TypeVar, Union

import numpy as np
from astropy.io.fits import BinTableHDU, HDUList, ImageHDU, PrimaryHDU, TableHDU
from astropy.table import Table

from . import detector as dtc
from .constants.fits import CCDID_LABEL, EXTNAME_LABEL
from .constants.misc import S_NON_FILENAMES
from .logging import getLogger

logger = getLogger(__name__)


def get_attr_with_index(obj: Any,
                        attr: str) -> Any:
    """Check for an index at the end of attr, using a regex which matches anything, followed by [, followed
    by a digit, followed by ]. If found, gets this index of the desired attribute.

    Parameters
    ----------
    obj : Any
        The object to whose attribute to get.
    attr : str
        The attribute to check, which may optionally end with an index, e.g. 'l_x[0]'.

    Returns
    -------
    Any
        The attribute, optionally indexed by the value provided in the string.

    Examples
    --------
    Let's say we have an object with an attribute 'l_x' which is a list of length 3. Calling this function
    as `get_attr_with_index(obj, 'l_x[0]')` would be equivalent to calling `obj.l_x[0]`.

    This function can also be used with an un-indexed attribute, e.g. calling this function as
    `get_attr_with_index(obj, 'l_x')` would be equivalent to calling `obj.l_x`.
    """

    regex_match = re.match(r"(.*)\[([0-9]+)]\Z", attr)

    if not regex_match:
        return getattr(obj, attr)

    # Get the attribute (matching group 1), indexed by the index (matching group 2)
    return getattr(obj, regex_match.group(1))[int(regex_match.group(2))]


def get_nested_attr(obj: Any,
                    attr: str) -> Any:
    """Gets a nested attribute of an object, e.g. `obj.a.b.c`

    Parameters
    ----------
    obj : Any
        The object whose attribute to get.
    attr : str
        The attribute to check, which may optionally be nested, e.g. 'a.b.c'. Each attribute may also optionally end
        with an index, e.g. 'a.b[0].c'.

    Returns
    -------
    Any
        The ultimate nested attribute.
    """

    if "." not in attr:
        return get_attr_with_index(obj, attr)

    head, tail = attr.split('.', 1)

    return get_nested_attr(get_attr_with_index(obj, head), tail)


def set_index_zero_attr(obj: Any,
                        attr: Any,
                        val: Any) -> None:
    """Deprecated in favor of `set_indexed_attr`."""
    if "[0]" not in attr:
        setattr(obj, attr, val)
    elif attr[-3:] == "[0]":
        getattr(obj, attr[:-3])[0] = val
    else:
        raise ValueError("Invalid format of attribute passed to get_attr_with_index: " + str(attr))


def set_attr_with_index(obj: Any,
                        attr: str,
                        val: Any) -> None:
    """Sets an attribute of an object, optionally indexed at some value, e.g. `set_indexed_attr(obj, 'l_x[0]', val)` is
    equivalent to `obj.l_x[0] = val`.

    Parameters
    ----------
    obj : Any
        The object whose attribute to set.
    attr : str
        The attribute whose value is to be set.
    val : Any
        The value to set the attribute to.
    """

    regex_match = re.match(r"(.*)\[([0-9]+)]\Z", attr)

    if not regex_match:
        setattr(obj, attr, val)
        return

    # Get the attribute (matching group 1), indexed by the index (matching group 2), and set it to the value
    getattr(obj, regex_match.group(1))[int(regex_match.group(2))] = val


def set_nested_attr(obj: Any,
                    attr: Any,
                    val: Any):
    """Sets a nested attribute of an object, e.g. `set_nested_attr(obj, 'a.b.c', val)` is equivalent to `obj.a.b.c =
    val`.

    Parameters
    ----------
    obj : Any
        The object whose attribute to set.
    attr : str
        The attribute to set, which may optionally be nested, e.g. 'a.b.c'. Each attribute may also optionally end
        with an index, e.g. 'a.b[0].c'.
    val : Any
        The value to set the attribute to.
    """

    if "." not in attr:
        set_attr_with_index(obj, attr, val)
        return

    head, tail = attr.split('.', 1)

    set_nested_attr(get_attr_with_index(obj, head), tail, val)


def get_release_from_version(version: str) -> str:
    """Gets a 'release' format string ('XX.XX' where X is 0-9) from a 'version' format string ('X.Y(.Z)',
       where XX is 0-99, and X, Y, and Z are any integers).

    Parameters
    ----------
    version : str
        The version string to convert (e.g. '1.1.0').

    Returns
    -------
    release : str
        The converted release string  (e.g. '01.01').
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
                   ccdid: Optional[str] = None) -> Optional[int]:
    """Find the index of the extension of a fits HDUList with the correct EXTNAME or CCDID value.

    Parameters
    ----------
    hdulist : HDUList
        The HDUList to search.
    extname : str, optional
        The EXTNAME value to search for. Either this or `ccdid` must be specified.
    ccdid : str, optional
        The CCDID value to search for. Either this or `extname` must be specified.
    """

    # Determine which key and value to search for based on what's been specified
    if extname is not None:
        val: str = extname
        key = EXTNAME_LABEL
    elif ccdid is not None:
        val: str = ccdid
        key = CCDID_LABEL
    else:
        raise ValueError("Either `extname` or `ccdid` must be supplied to the `find_extension` function.")

    for i, hdu in enumerate(hdulist):
        if key in hdu.header and hdu.header[key] == val:
            return i

    return None


def get_detector(obj: Union[TableHDU, BinTableHDU, ImageHDU, PrimaryHDU, Table]) -> Tuple[int, int]:
    """Find the detector indices for a fits hdu or table.

    Parameters
    ----------
    obj : Union[TableHDU, Table]
        The HDU or table to get the detector indices for.

    Returns
    -------
    Tuple[int, int]
        The indices of the detector.
    """

    # As long as typing conditions are met, the object will have either the header or meta attribute
    if hasattr(obj, "header"):
        header = obj.header
    else:
        header = obj.meta

    if EXTNAME_LABEL not in header:
        raise ValueError(f"Key '{EXTNAME_LABEL}' not found in header.")

    extname = header[EXTNAME_LABEL]

    detector_x = int(extname[dtc.x_index])
    detector_y = int(extname[dtc.y_index])

    return detector_x, detector_y


def get_all_files(directory_name: str) -> List[str]:
    """Search through a directory to get a full list of files in it and all of its sub-directories.

    Parameters
    ----------
    directory_name : str
        The name of the directory to search.

    Returns
    -------
    List[str]
        A list of all files in the directory, including its subdirectories.
    """
    # TODO: This should be moved to SHE_PPT.file_io

    full_file_list = []
    dir_list = [directory_name]

    is_complete = False

    while not is_complete:

        new_dir_list = []

        for dir_name in dir_list:

            file_list, sb_dir_list = _process_directory_for_files(dir_name)
            full_file_list += [os.path.join(dir_name, filename)
                               for filename in file_list]

            if sb_dir_list:
                new_dir_list += [os.path.join(dir_name, sb_dir)
                                 for sb_dir in sb_dir_list]

        dir_list = new_dir_list
        is_complete = len(dir_list) == 0

    return full_file_list


def _process_directory_for_files(directory_name: str) -> Tuple[List[str], List[str]]:
    """ Recursively check a directory for files; used within `get_all_files`.
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


def is_any_type_of_none(value: Union[None, str]) -> bool:
    """Quick function to check if a value (which might be a string) is None or empty.

    Parameters
    ----------
    value : Union[None, str]
        The value to test.

    Returns
    -------
    bool
        True if the value is of any type of None, False otherwise.
    """
    try:
        return value in S_NON_FILENAMES
    except (TypeError, ValueError):
        # We might get an exception if the value is of certain types, such as a numpy array. In that case,
        # it's not None as understood here, so return False
        return False


def is_inf(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Custom implementation if np.isinf check, which returns False for any masked values, unlike np.isinf, which
    returns masked for any masked values.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is inf or infinite, False otherwise.
    """
    # If no values are masked, we can simply forward to numpy
    if not np.ma.is_masked(x):
        return np.isinf(x)

    # For any masked values, return False. Otherwise we can use the result of np.isinf
    return np.where(is_masked(x), False, np.isinf(x))


def is_nan(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Custom implementation if np.isnan check, which returns False for any masked values, unlike np.isinf, which
    returns masked for any masked values.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is nan, False otherwise.
    """
    # If no values are masked, we can simply forward to numpy
    if not np.ma.is_masked(x):
        return np.isnan(x)

    # For any masked values, return False. Otherwise we can use the result of np.isnan
    return np.where(is_masked(x), False, np.isnan(x))


def is_masked(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Element-wise implementation of checking if an array is masked. `np.ma.is_masked` doesn't do this, as it always
    returns a summary bool of if any values are masked.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is masked, False otherwise.
    """
    # Test if the object is iterable, and if so, give element-wise results
    try:
        return np.array([np.ma.is_masked(item) for item in x])
    except TypeError:
        # It's not iterable, so test if the individual value is masked
        return np.ma.is_masked(x)


def any_is_inf(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is `inf`.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is `inf`, False otherwise.
    """
    return np.any(is_inf(l_x))


def any_is_nan(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is `nan`.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is `nan`, False otherwise.
    """
    return np.any(is_nan(l_x))


def any_is_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is masked. This can actually be done by a single function call with
    numpy, but this wrapper is presented here for consistency with `inf` and `nan` checks, so a user searching for a
    function to do this isn't left confused by its absence.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is masked, False otherwise.
    """
    return np.ma.is_masked(l_x)


def is_inf_or_nan(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Checks if a value is `inf` or `nan`.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is `inf` or `nan`, False otherwise.
    """
    return np.logical_or(is_inf(x), is_nan(x))


def any_is_inf_or_nan(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is `inf` or `nan`.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is `inf` or `nan`, False otherwise.
    """
    return np.any(is_inf_or_nan(l_x))


def is_nan_or_masked(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Checks if a value is `nan` or masked.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is `nan` or masked, False otherwise.
    """
    return np.logical_or(is_nan(x), is_masked(x))


def any_is_nan_or_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is `nan` or masked.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is `nan` or masked, False otherwise.
    """
    return np.any(is_nan_or_masked(l_x))


def is_inf_nan_or_masked(x: Union[float, Sequence[float]]) -> Union[bool, MutableSequence[bool]]:
    """Checks if a value is `inf`, `nan` or masked.

    Parameters
    ----------
    x : Union[float, Sequence[float]]
        The value to check.

    Returns
    -------
    Union[bool, Sequence[bool]]
        True if the value is `inf`, `nan` or masked, False otherwise.
    """
    return np.logical_or(is_inf(x), is_nan_or_masked(x))


def any_is_inf_nan_or_masked(l_x: Sequence[Union[float, Sequence[float]]]) -> bool:
    """Checks if any value in a sequence of values is `inf`, `nan` or masked.

    Parameters
    ----------
    l_x : Sequence[Union[float, Sequence[float]]]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is `inf`, `nan` or masked, False otherwise.
    """
    return np.any(is_inf_nan_or_masked(l_x))


Number = TypeVar('Number', float, int)


def is_zero(x: Number) -> bool:
    """ Checks if a value is zero - needed if a callable function is required to perform this test.

    Parameters
    ----------
    x : Number
        The value to check.

    Returns
    -------
    bool
        True if the value is zero, False otherwise.
    """
    return x == 0


def any_is_zero(l_x: Sequence[Number]) -> bool:
    """Checks if any value in a sequence of numbers is zero.

    Parameters
    ----------
    l_x : Sequence[Number]
        The sequence to check.

    Returns
    -------
    bool
        True if any value is zero, False otherwise.
    """

    return (np.asarray(l_x) == 0).any()


def all_are_zero(l_x: Sequence[Number]) -> bool:
    """Checks if all values in a sequence of numbers are zero.

    Parameters
    ----------
    l_x : Sequence[Number]
        The sequence to check.

    Returns
    -------
    bool
        True if all values are zero, False otherwise.
    """
    return (np.asarray(l_x) == 0).all()


# List/join and other collection functions

T = TypeVar('T')
TK = TypeVar('TK')
TV = TypeVar('TV')


# TODO: These default/empty_if... functions should probably be deprecated in favor of the ternary operator

def default_value_if_none(x: Optional[T],
                          default_x: T) -> T:
    """If input value is None, returns a provided default value, otherwise returns the input value.

    Parameters
    ----------
    x : Optional[T]
        The input value.
    default_x : T
        The default value to return if input `x` is None.

    Returns
    -------
    T
        The input value if it is not None, otherwise the default value.
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

    Parameters
    ----------
    x : Optional[Any]
        The input value.
    type : Type[T]
        The type to initialize if input `x` is None.
    args : Sequence[Any]
        The positional arguments to pass to the type's constructor.
    coerce : bool
        If True, the type is coerced to the input value's type.
    kwargs : Mapping[str, Any]
        The keyword arguments to pass to the type's constructor.

    Returns
    -------
    T
        The input value if it is not None, otherwise a default initialized value of the provided type.
    """
    if x is None:
        return type(*args, **kwargs)
    if coerce:
        x = type(x)
    return x


def empty_list_if_none(l_x: Optional[Sequence[T]],
                       coerce: bool = False) -> List[T]:
    """ If input value is None, constructs and returns an empty list, otherwise returns the input value.

    Parameters
    ----------
    l_x : Optional[Sequence[T]]
        The input value.
    coerce : bool
        If True, the input value is coerced to be a list.

    Returns
    -------
    List[T]
        The input value if it is not None, otherwise an empty list.
    """
    return default_init_if_none(l_x, list, coerce = coerce)


def empty_set_if_none(s_x: Optional[Union[Sequence[T], Set[T]]],
                      coerce: bool = False) -> Set[T]:
    """If input value is None, constructs and returns an empty set, otherwise returns the input value.

    Parameters
    ----------
    s_x : Optional[Union[Sequence[T], Set[T]]]
        The input value.
    coerce : bool
        If True, the input value is coerced to be a list.

    Returns
    -------
    Set[T]
        The input value if it is not None, otherwise an empty set.
    """
    return default_init_if_none(s_x, type = set, coerce = coerce)


def empty_dict_if_none(d_x: Optional[Dict[TK, TV]],
                       coerce: bool = False) -> Dict[TK, TV]:
    """ If input value is None, constructs and returns an empty dict, otherwise returns the input value.

    Parameters
    ----------
    d_x : Optional[Dict[TK, TV]]
        The input value.
    coerce : bool
        If True, the input value is coerced to be a dict.

    Returns
    -------
    Dict[TK, TV]
        The input value if it is not None, otherwise an empty dict.
    """
    return default_init_if_none(d_x, type = dict, coerce = coerce)


def coerce_to_list(a: Union[None, T, List[T]],
                   keep_none: bool = False) -> Union[List[T], None]:
    """Coerces either None, a single item, or a list to a list of items.

    Parameters
    ----------
    a : Union[None, T, List[T]]
        The input value.
    keep_none : bool
        If True, None is returned if input `a` is None. Otherwise an empty list is constructed and returned.

    Returns
    -------
    Union[List[T], None]
        The input value if it is not None, otherwise an empty list, unless the input is None and `keep_none` is True,
    """
    if a is None:
        l_a = None if keep_none else []
    elif isinstance(a, str):
        # Special handling for strings, which are iterable, but we don't want lists of their characters
        l_a = [a]
    else:
        # Check if it's iterable, and convert to list if so
        try:
            l_a = list(a)
        except TypeError:
            # Not iterable, so return as an element of a list
            l_a = [a]

    return l_a


def join_without_none(l_s: List[Optional[Any]],
                      joiner: str = "-",
                      default: Optional[str] = "") -> Optional[str]:
    """ Join a list of values into a single string, excepting any Nones.

    Parameters
    ----------
    l_s : List[Optional[Any]]
        The list of values to join.
    joiner : str
        The string to join the list elements with.
    default : Optional[str]
        The default string to return if the list is empty.

    Returns
    -------
    Optional[str]
        The joined string, or None if the list is empty.
    """

    # Get a list to join without any Nones
    l_s_no_none: List[str] = [str(s) for s in l_s if s is not None]

    # Return the default if the list is empty
    if len(l_s_no_none) == 0:
        return default

    # Otherwise, join the pieces
    return joiner.join(l_s_no_none)
