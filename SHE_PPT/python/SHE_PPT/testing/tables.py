""" @file testing/tables.py

    Created 14 December 2020

    Functions related to the testing of tables and table formats
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

from astropy.table import Column

import numpy as np

from ..table_utility import is_in_format


def _test_format_strict(empty_tables, l_tf, i, j):
    if i == j and not is_in_format(empty_tables[i], l_tf[j], strict=True):
        raise ValueError(f"Table format {l_tf[j].m.table_format} "
                         f"doesn't initialize a valid table in strict test.")
    if i != j and is_in_format(empty_tables[i], l_tf[j], strict=True):
        raise ValueError(f"Table format {l_tf[j].m.table_format} "
                         f"resolves true for tables of format {l_tf[i].m.table_format} "
                         f"in strict test.")


def _test_format_nonstrict(empty_tables, l_tf, i, j):
    if i == j and not is_in_format(empty_tables[i], l_tf[j], strict=False):
        raise ValueError(f"Table format {l_tf[j].m.table_format} "
                         f"doesn't initialize a valid table in non-strict test.")
    if i != j and is_in_format(empty_tables[i], l_tf[j], strict=False):
        raise ValueError(f"Table format {l_tf[j].m.table_format} "
                         f"resolves true for tables of format {l_tf[i].m.table_format} "
                         f"in non-strict test.")


def _test_is_in_format(l_tf):
    # Test each format is detected correctly

    empty_tables = []

    for tf in l_tf:
        empty_tables.append(tf.init_table())

    for i in range(len(l_tf)):

        # Try strict test
        for j in range((len(l_tf))):
            _test_format_strict(empty_tables, l_tf, i, j)

        # Try non-strict test now
        empty_tables[i].add_column(Column(name='new_column', data=np.zeros((0,))))
        for j in range((len(l_tf))):
            _test_format_nonstrict(empty_tables, l_tf, i, j)
