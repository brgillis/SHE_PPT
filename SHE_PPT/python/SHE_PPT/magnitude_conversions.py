""" @file magnitude_conversions.py

    Created 6 Oct 2015

    Functions to convert between Euclid magnitude and electron count
"""

__updated__ = "2021-08-12"

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

import numpy as np

from .constants.misc import MAG_I_ZEROPOINT, MAG_VIS_ZEROPOINT
from .gain import get_ADU_from_count


def get_count_from_mag_vis(m, exp_time):
    """ Gets the expected count from a magnitude using Euclid's magnitude zeropoint.

        @param m The input magnitude
        @param exp_time The exposure time

        @return The expected count
    """

    return exp_time * 10.0 ** (0.4 * (MAG_VIS_ZEROPOINT - m))


def get_mag_vis_from_count(c, exp_time):
    """ Gets the magnitude from the expected count using Euclid's magnitude zeropoint.

        @param c The input expected count
        @param exp_time The exposure time

        @return The magnitude
    """

    return MAG_VIS_ZEROPOINT - 2.5 * np.log10(c / exp_time)


def get_count_from_mag_i(m, exp_time):
    """ Gets the expected count from a magnitude using Euclid's magnitude zeropoint.

        @param m The input magnitude
        @param exp_time The exposure time

        @return The expected count
    """

    return exp_time * 10.0 ** (0.4 * (MAG_I_ZEROPOINT - m))


def get_mag_i_from_count(c, exp_time):
    """ Gets the magnitude from the expected count using Euclid's magnitude zeropoint.

        @param c The input expected count
        @param exp_time The exposure time

        @return The magnitude
    """

    return MAG_I_ZEROPOINT - 2.5 * np.log10(c / exp_time)


def get_intensity(intensity_parameter, parameter_type, gain, exp_time):
    """ Gets the measured intensity from the provided parameters

        @param c The input expected count
        @param exp_time The exposure time

        @return The measured intensity
    """

    intensity: float

    if parameter_type == 'intensity':
        intensity = intensity_parameter
    elif parameter_type == 'count':
        intensity = get_ADU_from_count(intensity_parameter, gain)
    elif parameter_type == 'flux':
        intensity = get_ADU_from_count(intensity_parameter * exp_time, gain)
    elif parameter_type == 'mag_vis':
        intensity = get_ADU_from_count(get_count_from_mag_vis(intensity_parameter, exp_time = exp_time), gain)
    elif parameter_type == 'mag_i':
        intensity = get_ADU_from_count(get_count_from_mag_i(intensity_parameter, exp_time = exp_time), gain)
    else:
        raise ValueError("get_I can't handle parameter type '" + str(parameter_type) + "'")

    return intensity
