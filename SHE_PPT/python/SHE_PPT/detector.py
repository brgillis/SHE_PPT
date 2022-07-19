""" @file detector.py

    Created 8 Nov 2017

    Magic values and functions related to detector IDs in FITS headers.
"""

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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

import numpy as np

id_template = "CCDID X-Y"

# Indices of x and y detector id in the detector string
x_index = 6
y_index = 8


def get_id_string(x, y):
    """Gets a detector ID string for a given x/y position.

    Parameters
    ----------
    x : int
        Detector position in the x dimension. Accepted values: 1-6
    y : int
        idem for y
    """

    # Check for valid values
    for v in x, y:
        if not isinstance(v, (int, np.int8)):
            raise TypeError(
                "Values passed to get_id_string must be int type: " + str(v) + ", type: " + str(type(v)))
        if v < 1 or v > 6:
            raise ValueError("Invalid value passed to get_id_string: " + str(v) + ", type: " + str(type(v)))

    return _get_id_string(x, y)


def _get_id_string(x, y):
    """Gets a detector ID string for a given x/y position, without checking
       for valid values.

    Parameters
    ----------
    x : int
        Detector position in the x dimension. Accepted values: 1-6
    y : int
        idem for y
    """

    return id_template.replace("X", str(int(x))).replace("Y", str(int(y)))


def get_detector_xy(id_string):
    """Gets the x and y position of a detector from its ID string.

    Parameters
    ----------
    id_string : str
        ID string (first part of EXTNAME header value for an HDU, or full EXTNAME)
    """

    if not isinstance(id_string, str):
        raise TypeError("id_string must be a string")
    if len(id_string) != len(id_template) and len(id_string) != len(id_template) + 4:
        raise ValueError("Improperly formatted id_string")

    return int(id_string[x_index]), int(id_string[y_index])


def detector_int_to_xy(i):
    """For handling depecrated definition of the detector, gives x/y position
    corresponding to an integer value.

    Parameters
    ----------
    i : int
        Integer detector value, in range 0-35
    """

    if not isinstance(i, int):
        raise TypeError("i must be of int type.")
    if i < 0 or i > 35:
        raise ValueError("i must be in range 0-35")

    return i % 6 + 1, i // 6 + 1


def detector_xy_to_int(x, y):
    """For handling depecrated definition of the detector, gives integer
    value from x/y position.

    Parameters
    ----------
    x : int
        Detector x position, in range 1-6
    y : int
        Detector x position, in range 1-6
    """

    for v in x, y:
        if not isinstance(v, int):
            raise TypeError(
                "Values passed to get_id_string must be int type: " + str(v))
        if v < 1 or v > 6:
            raise ValueError(
                "Invalid value passed to get_id_string: " + str(v))

    return 6 * (y - 1) + (x - 1)


def resolve_detector_xy(v):
    """Resolves detector_x/y from an object of string, int, or tuple type.

    Parameters
    ----------
    v : str, int, or (int,int)
        Value indicating detector
    """

    if isinstance(v, str):
        return get_detector_xy(v)
    if isinstance(v, int):
        return detector_int_to_xy(v)
    if isinstance(v, tuple) and len(v) == 2:
        return v
    raise TypeError("v must be int, string, or tuple[2] type.")


# Quadrant layout - note that due to column/row-major flip and the visual layout starting from bottom-left,
# this is transposed and flipped vertically compared to how the layout actually looks


QUADRANT_LAYOUT_123 = [["E", "H"],
                       ["F", "G"]]
QUADRANT_LAYOUT_456 = [["G", "F"],
                       ["H", "E"]]

VIS_DETECTOR_PIXELS_X = 4096
VIS_DETECTOR_PIXELS_Y = 4136


def get_vis_quadrant(x_pix: float,
                     y_pix: float,
                     det_iy: int):
    """ Get the letter signifying the quadrant of a VIS detector where a pixel coordinate is.
        Returns "X" if the position is outside of the detector bounds.

        This uses the charts at http://euclid.esac.esa.int/dm/dpdd/latest/le1dpd/dpcards/le1_visrawframe.html
        for its logic.
    """

    if x_pix <= -1 or y_pix <= -1:
        return "X"

    if det_iy <= 3:
        quadrant_layout = QUADRANT_LAYOUT_123
    else:
        quadrant_layout = QUADRANT_LAYOUT_456

    quad_ix = int(2 * x_pix / VIS_DETECTOR_PIXELS_X)
    quad_iy = int(2 * y_pix / VIS_DETECTOR_PIXELS_Y)

    if quad_ix in (0, 1) and quad_iy in (0, 1):
        quadrant = quadrant_layout[quad_ix][quad_iy]
    else:
        quadrant = "X"

    return quadrant
