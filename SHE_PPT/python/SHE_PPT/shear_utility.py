""" @file shear_utility.py

    Created 9 Feb, 2018

    Miscellaneous utility functions related to shear measurements
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

__updated__ = "2019-02-27"

import math


def get_g_from_e(e1, e2):
    """
    @brief
        Calculates the g-style shear from e-style

    @param e1
    @param e2

    @return g1, g2
    """

    e = math.sqrt(e1 * e1 + e2 * e2)
    beta = math.atan2(e2, e1)

    r2 = (1. - e) / (1. + e)

    r = math.sqrt(r2)

    g = (1. - r) / (1. + r)

    return g * math.cos(beta), g * math.sin(beta)
