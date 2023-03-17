""" @file __init__.py

    Created 24 Nov 2017
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

# noinspection PyUnresolvedReferences
import glob
import re

# noinspection PyUnresolvedReferences
from os.path import basename, dirname, isfile

# noinspection PyUnresolvedReferences
from SHE_PPT_VERSION import SHE_PPT_VERSION_STRING

from . import *  # noqa: F401,F403

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")]

del modules, dirname, basename, isfile, glob

# Get the version from the compiled file created by Elements
__version__ = SHE_PPT_VERSION_STRING

# Use this for passing into ST_DM_FilenameProvider.FilenameProvider.FileNameProvider
SHE_PPT_RELEASE_STRING = re.match(r"[0-9]{1,2}\.[0-9]{1,2}", SHE_PPT_VERSION_STRING).group()
