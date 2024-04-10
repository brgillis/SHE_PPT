"""
File: flags.py

Created on: 21 Feb, 2019

This module contains definitions of flag bits and fitclass values, as defined by
https://euclid.roe.ac.uk/projects/sgsshear/wiki/ShearMeasurementFlags
"""

import numpy as np

__updated__ = "2021-08-13"

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

# Flag format - increment version whenever there are non-trivial changes
# to this file

she_flag_version = "0.1"

# PSF model quality flags

flag_psf_quality_good = 0
flag_psf_quality_outside_fov = 1
flag_psf_quality_invalid = 2

# Fitclas values for what we believe the object is

fitclass_galaxy = 0
fitclass_star = 1
fitclass_unknown = 2

# Flag values for the status of an attempted shear estimation

flag_success = 0
flag_unclassified_failure = 2 ** 0
flag_no_data = 2 ** 1
flag_no_science_image = 2 ** 2
flag_corrupt_science_image = 2 ** 3
flag_no_mask = 2 ** 4
flag_corrupt_mask = 2 ** 5
flag_no_background_map = 2 ** 6
flag_corrupt_background_map = 2 ** 7
flag_no_noisemap = 2 ** 8
flag_corrupt_noisemap = 2 ** 9
flag_no_segmentation_map = 2 ** 10
flag_corrupt_segmentation_map = 2 ** 11
flag_insufficient_data = 2 ** 12
flag_inconsistent_exposures = 2 ** 13
flag_no_object = 2 ** 14
flag_not_centered = 2 ** 15
flag_too_crowded = 2 ** 16
flag_low_signal_to_noise = 2 ** 17
flag_object_too_small = 2 ** 18
flag_object_too_large = 2 ** 19
flag_no_psf = 2 ** 20
flag_corrupt_psf = 2 ** 21
flag_psf_too_small = 2 ** 22
flag_psf_too_large = 2 ** 23
flag_too_large_shear = 2 ** 24
flag_cannot_correct_distortion = 2 ** 25
flag_fitting_non_convergence = 2 ** 26
flag_invalid_calculation = 2 ** 27
flag_no_training_data = 2 ** 28
flag_corrupt_training_data = 2 ** 29
flag_no_calibration_data = 2 ** 30
flag_corrupt_calibration_data = 2 ** 31
flag_bad_calibration = 2 ** 32
flag_too_low_shape_error = 2 ** 33
flag_exposures_dropped = 2 ** 34

non_failure_flags = (flag_no_noisemap | flag_corrupt_noisemap | flag_no_segmentation_map |
                     flag_corrupt_segmentation_map | flag_too_low_shape_error | flag_exposures_dropped)
failure_flags = (2 ** 33 - 1) ^ non_failure_flags

# VIS flags for their flg data.
# See https://gitlab.euclid-sgs.uk/PF-VIS/VIS_ImageTools/-/blob/develop/VIS_ImageTools_M/python/VIS_ImageTools_M/FlagMap.py # noqa: E501
# where this code was lifted from (with minor PEP8 changes)...
# commit e5e5496a7aaeba8b003f2db7d0c3e903fafac26f, develop version 3.18
# Also see https://euclid.roe.ac.uk/projects/vis_pf/wiki/VIS_Flags though this is not always kept up to date :(

VIS_FLAGS = {
  # flag name           bit             hexadecimal  decimal      invalid
  'GOOD':          np.int32(0),        # 0x00000000 |          0 |
  'INVALID':       np.int32(1 << 0),   # 0x00000001 |          1 |
  'HOT':           np.int32(1 << 1),   # 0x00000002 |          2 | X
  'COLD':          np.int32(1 << 2),   # 0x00000004 |          4 | X
  'SAT':           np.int32(1 << 3),   # 0x00000008 |          8 | X
  'COSMIC':        np.int32(1 << 4),   # 0x00000010 |         16 | X
  'GHOST':         np.int32(1 << 5),   # 0x00000020 |         32 | X
  'QUADEDGE':      np.int32(1 << 6),   # 0x00000040 |         64 |
  'BAD_COLUMN':    np.int32(1 << 7),   # 0x00000080 |        128 | X
  'BAD_CLUSTER':   np.int32(1 << 8),   # 0x00000100 |        256 | X
  'CR_REGION':     np.int32(1 << 9),   # 0x00000200 |        512 | X
  'OVRCOL':        np.int32(1 << 12),  # 0x00001000 |      4,096 | X
  'CHARINJ':       np.int32(1 << 15),  # 0x00008000 |     32,768 | X
  'SATXTALKGHOST': np.int32(1 << 17),  # 0x00020000 |    131,072 | X
  'STARSIGNAL':    np.int32(1 << 18),  # 0x00040000 |    262,144 |
  'ADCMAX':        np.int32(1 << 21),  # 0x00200000 |  2,097,152 | X
  'NO_DATA':       np.int32(1 << 22),  # 0x00400000 |  4,194,304 | X
  'STITCHBLOCK':   np.int32(1 << 23),  # 0x00800000 |  8,388,608 |
  'OBJECTS':       np.int32(1 << 24),  # 0x01000000 | 16,777,216 |
}

# names of flags used to build the INVALID flag
INVALID_VIS_FLAG_NAMES = (
    'HOT', 'COLD', 'SAT', 'COSMIC', 'GHOST', 'BAD_COLUMN', 'BAD_CLUSTER',
    'CR_REGION', 'OVRCOL', 'CHARINJ', 'SATXTALKGHOST', 'ADCMAX', 'NO_DATA'
)

# INVALID flag bitmask is a bitwise OR of all invalid flags
INVALID_VIS_FLAGS = np.int32(np.bitwise_or.reduce([VIS_FLAGS[bitname] for bitname in INVALID_VIS_FLAG_NAMES]))


# Utility functions

def combine_flags(*flags):
    """ Returns an integer with the bit flags combined into one value.
    """

    combined_flags = 0

    for flag in flags:
        combined_flags |= flag

    return combined_flags


def is_flagged_with(a, flag):
    """ Checks if a value is flagged with a given bit or bits.
    """

    return bool(a & flag)


def is_not_flagged_with(a, flag):
    """ Checks if a value is not flagged with a given bit or bits.
    """

    return not bool(a & flag)


def is_flagged_failure(a):
    """ Checks if a value is flagged with a failure flag.
    """

    return is_flagged_with(a, failure_flags)


def is_not_flagged_failure(a):
    """ Checks if a value is not flagged with a failure flag.
    """

    return not is_flagged_failure(a)
