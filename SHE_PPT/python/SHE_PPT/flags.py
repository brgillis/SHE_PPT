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
# See https://gitlab.euclid-sgs.uk/PF-VIS/VIS_ImageTools/-/blob/develop/VIS_ImageTools_M/python/VIS_ImageTools_M/FlagMap.py (where this code was lifted from...)  # noqa: E501
# and https://euclid.roe.ac.uk/projects/vis_pf/wiki/VIS_Flags

VIS_FLAGS = {
  'GOOD':          np.int32(0x00000000),
  'INVALID':       np.int32(0x00000001),  # bit  0
  'HOT':           np.int32(0x00000002),  # bit  1
  'COLD':          np.int32(0x00000004),  # bit  2
  'SAT':           np.int32(0x00000008),  # bit  3
  'COSMIC':        np.int32(0x00000010),  # bit  4
  'GHOST':         np.int32(0x00000020),  # bit  5
  'OVRCOL':        np.int32(0x00001000),  # bit 12
  'EXTOBJ':        np.int32(0x00002000),  # bit 13
  'SCATLIGHT':     np.int32(0x00004000),  # bit 14
  'CHARINJ':       np.int32(0x00008000),  # bit 15
  'NEARCHARINJ':   np.int32(0x00010000),  # bit 16
  'SATXTALKGHOST': np.int32(0x00020000),  # bit 17
  'STARSIGNAL':    np.int32(0x00040000),  # bit 18
  'SATURATEDSTAR': np.int32(0x00080000),  # bit 19
  'CTICORRECTION': np.int32(0x00100000),  # bit 20
  'ADCMAX':        np.int32(0x00200000),  # bit 21
  'TXERROR':       np.int32(0x00400000),  # bit 22
  'STITCHBLOCK':   np.int32(0x00800000),  # bit 23
  'OBJECTS':       np.int32(0x01000000),  # bit 24
}

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
