#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
:file: tests/python/conftest.py

:date: 21/02/2023
:author: Gordon Gibb
"""

# Contains (and imports) fixtures required by SHE_PPT tests

import pytest

import os

from .she_io_fixtures import *


@pytest.fixture
def workdir(tmpdir):
    workdir = tmpdir

    # make the datadir
    datadir = os.path.join(workdir, "data")
    os.mkdir(datadir)

    return workdir
