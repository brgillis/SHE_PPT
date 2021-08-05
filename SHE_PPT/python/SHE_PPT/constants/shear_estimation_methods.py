""" @file shear_estimation_methods.py

    Created 6 Jan 2021

    Constants relating to shear estimation methods
"""

__updated__ = "2021-08-05"

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

from typing import List, Dict

from astropy.table import Table

from SHE_PPT.utility import AllowedEnum

from ..table_formats.she_ksb_measurements import tf as ksbm_tf
from ..table_formats.she_lensmc_measurements import tf as lmcm_tf
from ..table_formats.she_momentsml_measurements import tf as mmlm_tf
from ..table_formats.she_regauss_measurements import tf as regm_tf


class ShearEstimationMethods(AllowedEnum):
    KSB = "KSB"
    REGAUSS = "REGAUSS"
    MOMENTSML = "MomentsML"
    LENSMC = "LensMC"


D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS: Dict[ShearEstimationMethods, Table] = {
    ShearEstimationMethods.KSB: ksbm_tf,
    ShearEstimationMethods.REGAUSS: regm_tf,
    ShearEstimationMethods.MOMENTSML: mmlm_tf,
    ShearEstimationMethods.LENSMC: lmcm_tf}

NUM_METHODS: int = len(ShearEstimationMethods)
METHOD_NAMES: List[str] = [method_enum.value for method_enum in ShearEstimationMethods]
