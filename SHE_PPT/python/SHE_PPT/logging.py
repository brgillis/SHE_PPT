"""
    @file logging.py

    Created 11 Apr 2016

    Methods to get a logger automatically depending on if we're in an
    Elements project or not.
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

import logging
import os

try:
    import ElementsKernel.Logging as log
except ImportError:
    import logging as log


def getLogger(name):
    """
        @brief Forwards a request for a logger to the proper logging module.

        @param name
            The name of the program whose logger we want to get

        @returns
            The logger
    """
    return log.getLogger(str(name) + "[" + str(os.getpid()) + "]")


def set_log_level_debug():
    """ Convenience method to set log level to debug to make sure there aren't any issues with logging strings
    """
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
