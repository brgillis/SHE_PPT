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
:file: tests/python/hdf5_test.py

:date: 07/11/2022
:author: Gordon Gibb
"""

import pytest


class Testhdf5(object):
    @pytest.mark.skip(reason="Conversion is implicitly tested in vis_exposures_test")
    def test_conversion(self):
        # In vis_exposures_test.py, we check that the HDF5 VisExposure class returns the same values as the
        # FITS classes. This requires us to initially convert FITS to HDF5 (in one of the pytest fixtures)
        # which minimally tests that the conversion function does not fail. The tests on the VisExposures
        # classes check that astropy.fits, fitsio and HDF5 files all contain exectly the same data
        pass
