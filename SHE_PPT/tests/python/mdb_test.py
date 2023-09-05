""" @file mdb_test.py

    Created 15 Feb 2018

    Unit tests relating to MDB utility functions
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
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

__updated__ = "2021-08-12"

import logging
import os

import numpy as np
import pytest

from SHE_PPT import mdb
from SHE_PPT.testing.utility import SheTestCase


class TestMDB(SheTestCase):
    """Unit tests of the SHE_PPT.mdb module.
    """

    def setup_workdir(self):

        self._download_mdb()

    def post_setup(self):

        self.qualified_mdb_filename = os.path.join(self.workdir, self.mdb_filename)

        self.test_key = "SpaceSegment.Instrument.VIS.VISDetectorPixelLongDimensionFormat"
        self.test_detector = "1-2"
        self.test_quadrant = "E"

        self.ex_gain = 3.1
        self.ex_read_noise = 3.1307833277073978
        self.ex_read_noise_no_det = 3.3223757053329757
        self.ex_read_noise_no_quad = 3.1288953698554054
        self.ex_read_noise_no_det_no_quad = 3.3209775151504393

    @classmethod
    def teardown_class(cls):
        """Cleanup changes made during tests.
        """

        super().teardown_class()

        logging.disable(logging.NOTSET)

        mdb.reset()

    def test_get_mdb_details(self):
        """ Test that the mdb methods work when initialised
        """

        ex_value = 4136
        ex_description = 'This is the minimum number of pixels in the longest dimension of the VIS focal plane. Due ' \
                         'to the injection line inserted in the long                direction of the CCD format, ' \
                         'the active array is split in 2 equal active arrays, with 4 inactive pixels in the middle ' \
                         'for injection line.'
        ex_source = 'Input by J.A. As required. Not validated, for test in the MDB. EUCL-EST-PS-7-001.'
        ex_release = '0.2'
        ex_expression = None
        ex_unit = 'pixel'

        mdb.init(self.qualified_mdb_filename)
        assert mdb.get_mdb_value(self.test_key) == ex_value
        assert mdb.get_mdb_description(self.test_key) == ex_description
        assert mdb.get_mdb_source(self.test_key) == ex_source
        assert mdb.get_mdb_release(self.test_key) == ex_release
        assert mdb.get_mdb_expression(self.test_key) == ex_expression
        assert mdb.get_mdb_unit(self.test_key) == ex_unit

    def test_get_mdb_exceptions(self):
        """ Test that the mdb methods raise when not initialised
        """
        mdb.reset()

        with pytest.raises(RuntimeError):
            mdb.get_mdb_value(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_description(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_source(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_release(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_expression(self.test_key)
        with pytest.raises(RuntimeError):
            mdb.get_mdb_unit(self.test_key)

    def test_mdb_keys(self):
        """ Test that each key in the mdb_keys object corresponds to a real key in the MDB.
        """

        mdb.init(self.qualified_mdb_filename)

        # For each key we've assigned an attribute for
        for key_name in vars(mdb.mdb_keys):

            # Get the value of this attribute, which should be the up-to-date key name
            key = getattr(mdb.mdb_keys, key_name)

            # Try to get the value of this key in the MDB
            try:
                mdb.get_mdb_value(key)
            except KeyError:
                raise KeyError("Key \"" + key + "\" from mdb_keys attribute \"" + key_name + "\" not found in " +
                               "MDB dictionary. Check that it and the MDB are up-to-date.")

    def test_get_gain(self):
        """Test of the `get_gain` function.
        """

        mdb.init(self.qualified_mdb_filename)

        # Check we can get a single gain successfully

        gain = mdb.get_gain(detector=self.test_detector, quadrant=self.test_quadrant)
        assert np.isclose(gain, self.ex_gain)

        # Check that averaging works successfully

        # Disable warnings, since they're expected here
        logging.disable(logging.WARNING)

        gain = mdb.get_gain(quadrant=self.test_quadrant)
        assert np.isclose(gain, self.ex_gain)

        gain = mdb.get_gain(detector=self.test_detector)
        assert np.isclose(gain, self.ex_gain)

        gain = mdb.get_gain()
        assert np.isclose(gain, self.ex_gain)

        # Repeat the average tests to make sure they work with cached results

        gain = mdb.get_gain(quadrant=self.test_quadrant)
        assert np.isclose(gain, self.ex_gain)

        gain = mdb.get_gain(detector=self.test_detector)
        assert np.isclose(gain, self.ex_gain)

        gain = mdb.get_gain()
        assert np.isclose(gain, self.ex_gain)

    def test_get_read_noise(self):
        """Test of the `get_read_noise` function.
        """

        mdb.init(self.qualified_mdb_filename)

        read_noise = mdb.get_read_noise(detector=self.test_detector, quadrant=self.test_quadrant)
        assert np.isclose(read_noise, self.ex_read_noise)

        # Check that averaging works successfully

        # Disable warnings, since they're expected here
        logging.disable(logging.WARNING)

        read_noise = mdb.get_read_noise(quadrant=self.test_quadrant)
        assert np.isclose(read_noise, self.ex_read_noise_no_det)

        read_noise = mdb.get_read_noise(detector=self.test_detector)
        assert np.isclose(read_noise, self.ex_read_noise_no_quad)

        read_noise = mdb.get_read_noise()
        assert np.isclose(read_noise, self.ex_read_noise_no_det_no_quad)

        # Repeat the average tests to make sure they work with cached results
        read_noise = mdb.get_read_noise(quadrant=self.test_quadrant)
        assert np.isclose(read_noise, self.ex_read_noise_no_det)

        read_noise = mdb.get_read_noise(detector=self.test_detector)
        assert np.isclose(read_noise, self.ex_read_noise_no_quad)

        read_noise = mdb.get_read_noise()
        assert np.isclose(read_noise, self.ex_read_noise_no_det_no_quad)
