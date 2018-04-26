""" @file gain.py

    Created 6 Oct 2015

    Functions to convert between count and intensity using gain, since I
    can never seem to remember whether to multiply or divide by it.
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

def get_ADU_from_count(c, gain):
    """ Calculate the intensity in ADU from count with the given gain.

        @param c The electron count
        @param gain The gain in units of e-/ADU

        @return The intensity in units of ADU
    """

    return c / gain

def get_count_from_ADU(I, gain):
    """ Calculate the electron count from intensity in units of ADU with the given gain.

        @param I The intensity in units of ADU
        @param gain The gain in units of e-/ADU

        @return The count in units of e-
    """

    return I * gain
