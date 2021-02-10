"""
File: tests/python/mask_test.py

Created on: 26 Oct, 2017
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
# """This script gives a small demo of the image object.

__updated__ = "2019-02-27"


import logging
import os

import pytest

import SHE_PPT.mask as m
import numpy as np


logging.basicConfig(level=logging.DEBUG)


class Test_mask():

    @classmethod
    def setup_class(cls):

        cls.test_mask = np.array(((0, m.masked_near_edge, m.masked_off_image),
                                  (m.masked_bad_pixel, m.masked_near_edge, m.masked_off_image)),
                                 dtype=np.int32)

    @classmethod
    def teardown_class(cls):

        del cls.test_mask

    def test_as_bool(self):

        desired_bool_mask = np.array(((False, True, True),
                                      (True, True, True)),
                                     dtype=bool)

        assert (m.as_bool(self.test_mask) == desired_bool_mask).all()

    def test_is_masked_with(self):

        desired_bool_mask_1 = np.array(((False, True, False),
                                        (False, True, False)),
                                       dtype=bool)

        assert (m.as_bool(m.is_masked_with(self.test_mask, m.masked_near_edge)) == desired_bool_mask_1).all()

        desired_bool_mask_2 = np.array(((False, False, False),
                                        (True, False, False)),
                                       dtype=bool)

        assert (m.as_bool(m.is_masked_with(self.test_mask, m.masked_bad_pixel)) == desired_bool_mask_2).all()

        desired_bool_mask_3 = np.array(((False, False, True),
                                        (False, False, True)),
                                       dtype=bool)

        assert (m.as_bool(m.is_masked_with(self.test_mask, m.masked_off_image)) == desired_bool_mask_3).all()

    def test_is_masked_bad(self):

        desired_bool_mask = np.array(((False, False, True),
                                      (True, False, True)),
                                     dtype=bool)

        assert (m.as_bool(m.is_masked_bad(self.test_mask)) == desired_bool_mask).all()

    def test_is_masked_suspect(self):

        desired_bool_mask = np.array(((False, True, False),
                                      (False, True, False)),
                                     dtype=bool)

        assert (m.as_bool(m.is_masked_suspect(self.test_mask)) == desired_bool_mask).all()

    def test_is_masked_suspect_or_bad(self):

        desired_bool_mask = np.array(((False, True, True),
                                      (True, True, True)),
                                     dtype=bool)

        assert (m.as_bool(m.is_masked_suspect_or_bad(self.test_mask)) == desired_bool_mask).all()

    def test_is_not_masked_with(self):
        ol_mask = np.array(((False, True, True),
                            (True, True, True)),
                           dtype=bool)

        assert (m.as_bool(self.test_mask) == desired_bool_mask).all()

    def test_is_not_masked_with(self):

        desired_bool_mask_1 = ~np.array(((False, True, False),
                                         (False, True, False)),
                                        dtype=bool)

        assert (m.as_bool(m.is_not_masked_with(self.test_mask, m.masked_near_edge)) == desired_bool_mask_1).all()

        desired_bool_mask_2 = ~np.array(((False, False, False),
                                         (True, False, False)),
                                        dtype=bool)

        assert (m.as_bool(m.is_not_masked_with(self.test_mask, m.masked_bad_pixel)) == desired_bool_mask_2).all()

        desired_bool_mask_3 = ~np.array(((False, False, True),
                                         (False, False, True)),
                                        dtype=bool)

        assert (m.as_bool(m.is_not_masked_with(self.test_mask, m.masked_off_image)) == desired_bool_mask_3).all()

    def test_is_not_masked_bad(self):

        desired_bool_mask = ~np.array(((False, False, True),
                                       (True, False, True)),
                                      dtype=bool)

        assert (m.as_bool(m.is_not_masked_bad(self.test_mask)) == desired_bool_mask).all()

    def test_is_not_masked_suspect(self):

        desired_bool_mask = ~np.array(((False, True, False),
                                       (False, True, False)),
                                      dtype=bool)

        assert (m.as_bool(m.is_not_masked_suspect(self.test_mask)) == desired_bool_mask).all()

    def test_is_not_masked_suspect_or_bad(self):

        desired_bool_mask = ~np.array(((False, True, True),
                                       (True, True, True)),
                                      dtype=bool)

        assert (m.as_bool(m.is_not_masked_suspect_or_bad(self.test_mask)) == desired_bool_mask).all()
