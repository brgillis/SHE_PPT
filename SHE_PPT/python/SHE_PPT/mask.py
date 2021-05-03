"""
File: mask.py

Created on: 26 Oct, 2017

This module contains definitions of mask bits and various functions for testing
if a mask matches certain mask bits. All the functions return arrays in the
same data type as the mask array passed to them (or the tested mask bit if it's
of a larger dtype). If a bool array is desired to save space, the as_bool
function can be used to obtain this.
"""

#
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
#

__updated__ = "2019-02-27"


import numpy as np


# Mask format - increment version whenever there are non-trivial changes
# to this file
mask_fmt_label = "MSK_FMT_V"
mask_fmt_version = "0.2"

# Mask values - taken from definition at
# https://euclid.roe.ac.uk/projects/eucrma/wiki/ImageBitMasks?parent=20120410UserStories

masked_hot_pixel = 1
masked_cold_pixel = 2
masked_saturated_pixel = 4
masked_cosmic_ray = 8
masked_satellite_trail = 16
masked_interpolated_pixel = 32
masked_bleeding = 64
masked_onboard = 128
masked_bad_pixel = 256
masked_nonlinear_pixel = 512
masked_persistent_charge_pixel = 1024
masked_ghost = 2048
masked_transient_object = 4096
masked_extended_object = 8192
masked_scattered_light = 16483
masked_charge_injection = 32768
masked_near_charge_injection = 65536
masked_off_image = 131072
masked_near_edge = 262144

# Some compiled mask values for all "bad" or "suspect" cases

masked_bad = (masked_hot_pixel | masked_cold_pixel | masked_saturated_pixel | masked_cosmic_ray |
              masked_satellite_trail | masked_bleeding | masked_onboard | masked_bad_pixel |
              masked_nonlinear_pixel | masked_persistent_charge_pixel | masked_ghost |
              masked_transient_object | masked_extended_object | masked_scattered_light |
              masked_charge_injection | masked_off_image)
masked_suspect = (masked_near_charge_injection | masked_near_edge)

masked_suspect_or_bad = masked_suspect | masked_bad


def as_bool(a):
    """Converts a scalar int into a bool or an array of ints into an array of bools.

    Parameters
    ----------
    a : scalar int or array of ints

    Returns
    -------
    bool or array of bools
    """

    if np.isscalar(a):
        return bool(a)
    return a.astype(bool)

# Various convenience functions to return bools (or arrays of bools) based
# on a mask test


def is_masked_with(a, mask_value):
    """ Tests if a mask matches a particular mask value (or combination). Mostly so that
    users don't have to worry about bit-comparison syntax.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test
    mask_value : int
        Integer mask value to test against

    Returns
    -------
    np.ndarray<int>
        Array with non-zero values for pixels which match the supplied mask value, zero for other pixels.
    """

    return a & mask_value


def is_masked_bad(a):
    """ Tests if a mask matches the mask for all possible bad (but not just suspect) bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<int>
        Array with non-zero values for bad pixels, zero values for good or suspect pixels.
    """

    return a & masked_bad


def is_masked_suspect(a):
    """ Tests if a mask matches the mask for all possible suspect (but not bad) bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<int>
        Array with non-zero values for suspect pixels, zero values for good or bad pixels.
    """

    return a & masked_suspect


def is_masked_suspect_or_bad(a):
    """ Tests if a mask matches the mask for all possible suspect or bad bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<int>
        Array with non-zero values for bad or suspect pixels, zero values for good pixels.
    """

    return a & masked_suspect_or_bad

# Inverse mask tests - will return true if not masked


def is_not_masked_with(a, mask_value):
    """ Tests if a mask does not match a particular mask value (or combination). Mostly so that
    users don't have to worry about bit-comparison syntax.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test
    mask_value : int
        Integer mask value to test against

    Returns
    -------
    np.ndarray<bool>
        Array with False for pixels which match the supplied mask value, True for other pixels.
    """

    return np.logical_not(a & mask_value)


def is_not_masked_bad(a):
    """ Tests if a mask does not match the mask for all possible bad (but not just suspect) bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<bool>
        Array with False for bad pixels, True for good or suspect pixels.
    """

    return np.logical_not(a & masked_bad)


def is_not_masked_suspect(a):
    """ Tests if a mask does not match the mask for all possible suspect (but not bad) bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<bool>
        Array with False for suspect pixels, True for good or bad pixels.
    """

    return np.logical_not(a & masked_suspect)


def is_not_masked_suspect_or_bad(a):
    """ Tests if a mask does not match the mask for all possible suspect or bad bits.

    Parameters
    ----------
    a : np.ndarray<int>
        Integer mask array to test

    Returns
    -------
    np.ndarray<bool>
        Array with False for bad or suspect pixels, True for good pixels.
    """

    return np.logical_not(a & masked_suspect_or_bad)
