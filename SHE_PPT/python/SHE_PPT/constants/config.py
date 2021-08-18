""" @file test_data.py

    Created 12 Aug 2021

    Constants used for miscellaneous purposes
"""

__updated__ = "2021-08-18"

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

from typing import Any, Dict, Union, Tuple, Type
from SHE_PPT.pipeline_utility import ConfigKeys, GlobalConfigKeys


# Set up dicts for pipeline config defaults and types
D_GLOBAL_CONFIG_DEFAULTS: Dict[ConfigKeys, Any] = {
    GlobalConfigKeys.PIP_PROFILE: False,
}

D_GLOBAL_CONFIG_TYPES: Dict[ConfigKeys, Union[Type, Tuple[Type, Type]]] = {
    GlobalConfigKeys.PIP_PROFILE: bool,
}

D_GLOBAL_CONFIG_CLINE_ARGS: Dict[ConfigKeys, str] = {
    GlobalConfigKeys.PIP_PROFILE: "profile",
}
