""" @file constants/classes.py

    Created 12 Aug 2021

    Classed and Enums used to hold constant values.
"""

from __future__ import annotations

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

from enum import Enum
from typing import Any, Optional


class AllowedEnum(Enum):
    """An extension of the base Enum class with methods to check if a value is allowed, or to find a value."""

    @classmethod
    def is_allowed_value(cls, value: str) -> bool:
        return value in [item.value for item in cls]

    @classmethod
    def find_value(cls, value: Any) -> Optional[AllowedEnum]:
        for item in cls:
            if item.value == value:
                return item
        return None

    @classmethod
    def find_lower_value(cls, lower_value: str) -> Optional[AllowedEnum]:
        for item in cls:
            if item.value.lower() == lower_value:
                return item
        return None


class PhotozCatalogMethods(AllowedEnum):
    PHOTOZ = "PhotoZCatalog"
    CLASSIFICATION = "ClassificationCatalog"
    GALSED = "GalaxySedCatalog"
    STARSED = "StarSedCatalog"
    PHYSPARAM = "PhysicalParametersCatalog"


class ShearEstimationMethods(AllowedEnum):
    KSB = "KSB"
    REGAUSS = "REGAUSS"
    MOMENTSML = "MomentsML"
    LENSMC = "LensMC"


class BinParameters(AllowedEnum):
    """Enum of possible binning parameters for test cases."""

    TOT = "tot"
    SNR = "snr"
    BG = "bg"
    COLOUR = "colour"
    SIZE = "size"
    EPOCH = "epoch"
