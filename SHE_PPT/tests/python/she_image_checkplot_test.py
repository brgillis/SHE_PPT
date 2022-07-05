"""
File: tests/python/she_image_checkplot_test.py

Created on: 10/19/17
Author: Malte Tewes
"""

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

__updated__ = "2021-08-16"

import logging
import os

import numpy as np
import pytest

import SHE_PPT.she_image
import SHE_PPT.she_image_checkplot
# Disable tests if we don't have a display
from SHE_PPT.testing.utility import SheTestCase

if 'DISPLAY' in os.environ:
    disable_tests = False
else:
    disable_tests = True

logging.basicConfig(format = '%(levelname)s: %(name)s(%(funcName)s): %(message)s', level = logging.DEBUG)


class TestSheImageCheckplot(SheTestCase):
    """
    @class Testshe_image_checkplot
    @brief Unit Test class
    """

    @classmethod
    def setup_test_data(cls):
        cls.testfilepath = "test_checkplot.png"

    @classmethod
    def teardown_class(cls):
        return
        if os.path.exists(cls.testfilepath):
            os.remove(cls.testfilepath)

    @pytest.mark.skip(reason = "No display available on CODEEN, so not expected to work on master branch")
    def test_checkplot(self):
        """

        """

        if disable_tests:
            return

        # Get some SHEImage

        array = np.random.randn(30, 20)
        array[4, 2] = 10
        mask = np.zeros(array.shape, dtype = bool)
        mask[10:15, :] = True
        img = SHE_PPT.she_image.SHEImage(array, mask = mask)

        checkplot = SHE_PPT.she_image_checkplot.Checkplot(img, scale = 20)
        checkplot.save_to_file(self.testfilepath)

    @pytest.mark.skip(reason = "No display available on CODEEN, so not expected to work on master branch")
    def test_checkplot_interactive(self):
        """Don't leave this function in production tests!
        It's purpose is more to demonstrate and play with new checkplot features!
        """

        (X, Y) = np.mgrid[0:30, 0:20]
        array = np.sin(0.3 * X) + np.sin(0.2 * Y) + 0.3 * np.random.randn(30, 20)
        mask = np.zeros(array.shape, dtype = bool)
        mask[22:25, 5:12] = True
        img = SHE_PPT.she_image.SHEImage(array, mask = mask)

        checkplot = SHE_PPT.she_image_checkplot.Checkplot(img, z1 = -1.5, z2 = 1.5, scale = 15)
        checkplot.save_to_file("/home/user/Desktop/img.png")

        stamp = img.extract_stamp(0.5, 0.5, 5)
        checkplot = SHE_PPT.she_image_checkplot.Checkplot(stamp, z1 = -1.5, z2 = 1.5, scale = 20)
        checkplot.save_to_file("/home/user/Desktop/stamp1.png")

        stamp = img.extract_stamp(30.5, 10.5, 30, 40)
        checkplot = SHE_PPT.she_image_checkplot.Checkplot(stamp, z1 = -1.5, z2 = 1.5, scale = 10)
        checkplot.save_to_file("/home/user/Desktop/stamp2.png")

        return
