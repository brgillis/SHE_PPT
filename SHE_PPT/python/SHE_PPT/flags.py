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
flag_corrupt_data = 2**2
flag_insufficient_data = 2**3
flag_inconsistent_exposures = 2**4
flag_no_object = 2**5
flag_not_centered = 2**6
flag_too_crowded = 2**7
flag_low_signal_to_noise = 2**8
flag_object_too_small = 2**9
flag_object_too_large = 2**10
flag_no_psf = 2**11
flag_corrupt_psf = 2**12
flag_psf_too_small = 2**13
flag_psf_too_large = 2**14
flag_too_large_shear = 2**15
flag_cannot_correct_distortion = 2**16
flag_fitting_non_convergence = 2**17
flag_invalid_calculation = 2**18
flag_no_training_data = 2**19
flag_corrupt_training_data = 2**20
flag_no_calibration_data = 2**21
flag_corrupt_calibration_data = 2**22
flag_bad_calibration = 2**23
