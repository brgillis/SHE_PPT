""" @file le1_aocs_time_series.py

    Created 10 Oct 2017

    Functions to create and output an aocs_time_series data product.
    This describes the series of pointing errors over the course of an observation

    Origin: OU-VIS (presumably - might need to put in a ticket to request it from them.
    Not actually used at present though, so we don't need it for SC4)
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA

__updated__ = "2021-06-09"

import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider

from ..file_io import read_xml_product, find_aux_file
from ..product_utility import get_data_filename_from_product, set_data_filename_of_product, init_placeholder_general


sample_file_name = 'SHE_PPT/sample_placeholder_general.xml'


def init():
    """
        TODO: Fill in docstring

    """

    init_placeholder_general()

    return


def create_dpd_le1_aocs_time_series(filename="None"):
    """
        @TODO fill in docstring
    """

    dpd_le1_aocs_time_series = read_xml_product(
        find_aux_file(sample_file_name))

    # Set the data we don't need to empty
    dpd_le1_aocs_time_series.Data.IntData = []
    dpd_le1_aocs_time_series.Data.FloatData = []

    # Label the type in the StringData
    dpd_le1_aocs_time_series.Data.StringData = ["TYPE:DpdLe1AocsTimeSeries"]

    dpd_le1_aocs_time_series.Header = HeaderProvider.create_generic_header("DpdShePlaceholderGeneral")

    if filename:
        dpd_le1_aocs_time_series.set_data_filename(filename)

    return dpd_le1_aocs_time_series


# Add a useful alias
create_aocs_time_series_data_product = create_dpd_le1_aocs_time_series
