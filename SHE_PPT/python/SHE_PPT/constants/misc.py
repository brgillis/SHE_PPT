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

SHORT_INSTANCE_ID_MAXLEN = 17

# Segmentation map
SEGMAP_UNASSIGNED_VALUE = 0
SEGMAP_OTHER_VALUE = -1

# Instrument zeropoints

# MAG_VIS_ZEROPOINT = 25.50087633632 # From ETC
# MAG_VIS_ZEROPOINT = 25.4534 # From Sami's sims' config file
MAG_VIS_ZEROPOINT = 25.6527  # From Lance's code
MAG_I_ZEROPOINT = 25.3884  # From Lance's code
DEFAULT_WORKDIR = "."

# Constant string for the data subdirectory, where datafiles are expected to be stored during pipeline execution
DATA_SUBDIR = "data/"

# Constant string to represent that a file does not exist
FILENAME_NONE = "None"

# Constant set of values which correspond to no file being present
S_NON_FILENAMES = {None, FILENAME_NONE, f"{DATA_SUBDIR}{FILENAME_NONE}", "", DATA_SUBDIR}
