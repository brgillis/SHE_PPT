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

__updated__ = "2020-06-16"

# import ST_DM_HeaderProvider.GenericHeaderProvider as HeaderProvider # FIXME
# import ST_DataModelBindings.she.she_stub as she_dpd # FIXME

import pickle


def init():
    """
        Adds some extra functionality to the DpdLe1AocsTimeSeriesProduct product
    """

    # binding_class = she_dpd.DpdLe1AocsTimeSeriesProduct # @FIXME
    binding_class = DpdLe1AocsTimeSeriesProduct

    binding_class.get_all_filenames = __get_all_filenames

    binding_class.has_files = False

    return


def __get_all_filenames(self):

    all_filenames = []

    return all_filenames


class DpdLe1AocsTimeSeriesProduct:  # @FIXME

    def __init__(self):
        self.Header = None
        self.Data = None

    def validateBinding(self):
        return False


class Le1AocsTimeSeriesProduct:  # @FIXME

    def __init__(self):
        pass


def create_dpd_le1_aocs_time_series():
    """
        @TODO fill in docstring
    """

    # dpd_le1_aocs_time_series = she_dpd.DpdLe1AocsTimeSeriesProduct() # @FIXME
    dpd_le1_aocs_time_series = DpdLe1AocsTimeSeriesProduct()

    # dpd_le1_aocs_time_series.Header =
    # HeaderProvider.create_generic_header("SHE") # FIXME
    dpd_le1_aocs_time_series.Header = "SHE"

    dpd_le1_aocs_time_series.Data = create_le1_aocs_time_series()

    return dpd_le1_aocs_time_series


# Add a useful alias
create_aocs_time_series_product = create_dpd_le1_aocs_time_series


def create_le1_aocs_time_series():
    """
        @TODO fill in docstring
    """

    # le1_aocs_time_series = she_dpd.Le1AocsTimeSeriesProduct() # @FIXME
    le1_aocs_time_series = Le1AocsTimeSeriesProduct()

    return le1_aocs_time_series
