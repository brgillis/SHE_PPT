"""
File: tests/python/she_image_stack_test.py

Created on: 09/01/17
"""

__updated__ = "2021-08-16"

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

import os
from copy import deepcopy

import numpy as np

from SHE_PPT.she_image import SHEImage
from SHE_PPT.she_image_stack import SHEImageStack
from SHE_PPT.testing.utility import SheTestCase


class TestSheImageStack(SheTestCase):

    def post_setup(self):
        # Filenames for testing the file io, will be deleted by teardown_class
        self.sci_filepath_1 = "test_SHEImageStack_sci_SHEImage.fits"
        self.sci_filepath_2 = "test_SHEImageStack_sci_SHEImage2.fits"

    def test_read(self):
        """We create the minimum required files, and read a SHEImageStack"""

        # Create what will be one exposure:
        sci_image_1 = SHEImage(np.random.randn(100).reshape(10, 10))
        sci_image_2 = SHEImage(np.random.randn(100).reshape(10, 10))

        # Save those to files:
        sci_image_1.write_to_fits(self.sci_filepath_1)
        sci_image_2.write_to_fits(self.sci_filepath_2)

        # Read this, directly as a SHEImageStack

        filepaths_list = [
            [self.sci_filepath_1],
            [self.sci_filepath_2]
            ]

        mystack = SHEImageStack.read(filepaths_list, mask_ext='MASK')  # Testing kwargs as well
        print(mystack.exposures[0])

    def test_equality(self):
        # Test we get equal when we expect it
        sci_image_1 = SHEImage(np.random.randn(100).reshape(10, 10))
        sci_image_2 = SHEImage(np.random.randn(100).reshape(10, 10))
        sci_image_s = SHEImage(np.random.randn(100).reshape(10, 10))

        stack = SHEImageStack(stacked_image=sci_image_s, exposures=[sci_image_1, sci_image_2])

        stack_copy = deepcopy(stack)
        assert stack == stack_copy

        # Test we get inequal when we change the copy
        stack_copy.stacked_image.data += 1
        assert stack != stack_copy
