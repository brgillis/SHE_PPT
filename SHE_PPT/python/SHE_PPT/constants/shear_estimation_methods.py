""" @file shear_estimation_methods.py

    Created 6 Jan 2021

    Constants relating to shear estimation methods
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

from typing import Dict, List

# Need to import ShearEstimationMethods first to avoid circular dependencies. We import explicitly to ensure it's
# sorted to be imported first
from SHE_PPT.constants.classes import ShearEstimationMethods
from ..table_formats.she_ksb_measurements import tf as ksbm_tf
from ..table_formats.she_ksb_tu_matched import tf as ksbtm_tf
from ..table_formats.she_lensmc_measurements import tf as lmcm_tf
from ..table_formats.she_lensmc_tu_matched import tf as lmctm_tf
from ..table_formats.she_measurements import SheMeasurementsFormat
from ..table_formats.she_momentsml_measurements import tf as mmlm_tf
from ..table_formats.she_momentsml_tu_matched import tf as mmltm_tf
from ..table_formats.she_regauss_measurements import tf as regm_tf
from ..table_formats.she_regauss_tu_matched import tf as regtm_tf
from ..table_formats.she_tu_matched import SheTUMatchedFormat

D_SHEAR_ESTIMATION_METHOD_TABLE_FORMATS: Dict[ShearEstimationMethods, SheMeasurementsFormat] = {
    ShearEstimationMethods.KSB: ksbm_tf,
    ShearEstimationMethods.REGAUSS: regm_tf,
    ShearEstimationMethods.MOMENTSML: mmlm_tf,
    ShearEstimationMethods.LENSMC: lmcm_tf}

D_SHEAR_ESTIMATION_METHOD_TUM_TABLE_FORMATS: Dict[ShearEstimationMethods, SheTUMatchedFormat] = {
    ShearEstimationMethods.KSB: ksbtm_tf,
    ShearEstimationMethods.REGAUSS: regtm_tf,
    ShearEstimationMethods.MOMENTSML: mmltm_tf,
    ShearEstimationMethods.LENSMC: lmctm_tf}

NUM_METHODS: int = len(ShearEstimationMethods)
METHOD_NAMES: List[str] = [method_enum.value for method_enum in ShearEstimationMethods]
