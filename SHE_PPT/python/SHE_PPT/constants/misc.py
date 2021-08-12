""" @file test_data.py

    Created 12 Aug 2021

    Constants used for miscellaneous purposes
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

short_instance_id_maxlen = 17

# Segmentation map
segmap_unassigned_value = 0
segmap_other_value = -1

# Instrument zeropoints

# mag_vis_zeropoint = 25.50087633632 # From ETC
# mag_vis_zeropoint = 25.4534 # From Sami's sims' config file
mag_vis_zeropoint = 25.6527  # From Lance's code
mag_i_zeropoint = 25.3884  # From Lance's code
