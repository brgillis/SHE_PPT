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
from Program_Files.GalSim.devel.external.update_parametric_fits import failure

"""
File: flags.py

Created on: 21 Feb, 2019

This module contains definitions of flag bits and fitclass values.
"""

import numpy as np


# Flag format - increment version whenever there are non-trivial changes
# to this file

flag_fmt_label = "FLG_FMT_V"
flag_fmt_version = "0.1"


# Fitclas values for what we believe the object is

fitclass_galaxy = 0
fitclass_star = 1
fitclass_unknown = 2


# Flag values for the status of an attempted shear estimation

flag_success = 0
flag_unclassified_failure = 2**0
flag_no_data = 2**1
flag_no_science_image = 2**2
flag_corrupt_science_image = 2**3
flag_no_mask = 2**4
flag_corrupt_mask = 2**5
flag_no_background_map = 2**6
flag_corrupt_background_map = 2**7
flag_no_noisemap = 2**8
flag_corrupt_noisemap = 2**9
flag_no_segmentation_map = 2**10
flag_corrupt_segmentation_map = 2**11
flag_insufficient_data = 2**12
flag_inconsistent_exposures = 2**13
flag_no_object = 2**14
flag_not_centered = 2**15
flag_too_crowded = 2**16
flag_low_signal_to_noise = 2**17
flag_object_too_small = 2**18
flag_object_too_large = 2**19
flag_no_psf = 2**20
flag_corrupt_psf = 2**21
flag_psf_too_small = 2**22
flag_psf_too_large = 2**23
flag_too_large_shear = 2**24
flag_cannot_correct_distortion = 2**25
flag_fitting_non_convergence = 2**26
flag_invalid_calculation = 2**27
flag_no_training_data = 2**28
flag_corrupt_training_data = 2**29
flag_no_calibration_data = 2**30
flag_corrupt_calibration_data = 2**31
flag_bad_calibration = 2**32

non_failure_flags = (flag_no_noisemap | flag_corrupt_noisemap | flag_no_segmentation_map |
                     flag_corrupt_segmentation_map | flag_not_centered)
failure_flags = (2**33 - 1) ^ non_failure_flags


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
