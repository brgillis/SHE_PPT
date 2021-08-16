""" @file le1_aocs_time_series.py

    Created 10 Oct 2017

    Functions to create and output an aocs_time_series data product.
    This describes the series of pointing errors over the course of an observation

    Origin: OU-VIS (presumably - might need to put in a ticket to request it from them.
    Not actually used at present though, so we don't need it for SC4)
"""

__updated__ = "2021-08-16"

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

from ..product_utility import init_placeholder_general, create_general_product_from_template


sample_file_name = 'SHE_PPT/sample_placeholder_general.xml'


def init():
    """
        TODO: Fill in docstring

    """

    init_placeholder_general(init_function=create_dpd_le1_aocs_time_series)


def create_dpd_le1_aocs_time_series(filename="None"):
    """
        @TODO fill in docstring
    """

    return create_general_product_from_template(template_filename=sample_file_name,
                                                product_name="DpdLe1AocsTimeSeries",
                                                filename=filename,)


# Add a useful alias
create_aocs_time_series_data_product = create_dpd_le1_aocs_time_series
