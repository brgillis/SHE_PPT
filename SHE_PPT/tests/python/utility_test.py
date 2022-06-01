""" @file utility_test.py

    Created 25 Aug 2017

    Unit tests relating to utility functions.
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

__updated__ = "2021-02-10"

import os
import shutil
from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

import numpy as np

from SHE_PPT.testing.utility import SheTestCase
from SHE_PPT.utility import (_process_directory_for_files, any_is_inf_nan_or_masked, any_is_inf_or_nan,
                             any_is_nan_or_masked, get_all_files, get_attr_with_index, get_nested_attr, is_inf,
                             is_inf_nan_or_masked,
                             is_inf_or_nan, is_masked, is_nan, is_nan_or_masked, set_attr_with_index, set_nested_attr, )


@dataclass
class MockClass:
    """A mock class to test the utility functions which deal with setting/getting attrs.
    """
    a: int = 0
    b: float = 1.1
    c: str = "2.2.2"
    d: bool = False
    e: np.ndarray = np.array([1, 2, 3])
    r: "Optional[MockClass]" = None


class TestUtility(SheTestCase):
    """Class to handle unit tests for functions in the `SHE_PPT.utility` module.
    """

    def post_setup(self):
        """Set up some data used in multiple tests.
        """

        # Create an object of the MockClass type, with a complicated nested structure
        mock_object_s2 = MockClass()
        mock_object_s1 = MockClass(r = mock_object_s2)
        self.mock_object = MockClass(r = mock_object_s1)

    def test_get_attr_with_index(self):
        """Unit test of the `get_nested_attr` function.
        """

        # Test getting a simple attribute
        assert get_attr_with_index(self.mock_object, 'a') == self.mock_object.a

        # Test getting an indexed attribute
        assert get_attr_with_index(self.mock_object, 'e[1]') == self.mock_object.e[1]

    def test_get_nested_attr(self):
        """Unit test of the `get_nested_attr` function.
        """

        # Test getting a simple attribute
        assert get_nested_attr(self.mock_object, 'a') == self.mock_object.a

        # Test getting a nested attribute
        assert get_nested_attr(self.mock_object, 'r.b') == self.mock_object.r.b

        # Test getting a nested indexed attribute
        assert get_nested_attr(self.mock_object, 'r.e[1]') == self.mock_object.r.e[1]

    def test_set_attr_with_index(self):
        """Unit test of the `set_nested_attr` function.
        """

        copied_object = deepcopy(self.mock_object)

        # Test setting a simple attribute
        set_attr_with_index(copied_object, 'a', 2)
        assert copied_object.a == 2

        # Test setting an indexed attribute
        set_attr_with_index(copied_object, 'e[1]', 3)
        assert copied_object.e[1] == 3

    def test_set_nested_attr(self):
        """Unit test of the `set_nested_attr` function.
        """

        copied_object = deepcopy(self.mock_object)

        # Test setting a simple attribute
        set_attr_with_index(copied_object, 'a', 2)
        assert copied_object.a == 2

        # Test setting a nested attribute
        set_nested_attr(copied_object, 'r.b', 2.2)
        assert copied_object.r.b == 2.2

        # Test setting a nested indexed attribute
        set_nested_attr(copied_object, 'r.r.e[0]', 3.2)
        assert copied_object.r.r.e[0] == 3.2

    def test_process_directory(self):
        """Unit test of the `process_directory` function.
        """
        test_dir = os.path.join(self.workdir, 'fgdyteihth')
        os.mkdir(test_dir)
        subdir_name1 = 'sub_a'
        os.mkdir(os.path.join(test_dir, subdir_name1))
        # subdir_name2='sub_b'
        # os.mkdir(os.path.join(test_dir,subdir_name2))
        file_name1 = 'file1.txt'
        file_name2 = 'file2.txt'
        open(os.path.join(test_dir, file_name1), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, file_name2), 'w').writelines(['2\n'])
        file_list, sbdir_list = _process_directory_for_files(test_dir)
        assert len(file_list) == 2
        assert len(sbdir_list) == 1
        shutil.rmtree(test_dir)

    def test_get_all_files(self):
        """Unit test of the `get_all_files` function.
        """
        test_dir = os.path.join(self.workdir, 'fgdytedggdsth')
        os.mkdir(test_dir)
        subdir_name1 = 'sub_a'
        os.mkdir(os.path.join(test_dir, subdir_name1))
        subdir_name2 = 'sub_b'
        os.mkdir(os.path.join(test_dir, subdir_name2))
        file_name1 = 'file1.txt'
        file_name2 = 'file2.txt'
        open(os.path.join(test_dir, file_name1), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, file_name2), 'w').writelines(['2\n'])
        file_name3 = 'file3.txt'
        file_name4 = 'file4.txt'
        open(os.path.join(test_dir, subdir_name1, file_name3), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, subdir_name2, file_name4), 'w').writelines(['2\n'])
        subdir_name3 = 'sub_b1'
        os.mkdir(os.path.join(test_dir, subdir_name2, subdir_name3))
        file_name5 = 'file5.txt'
        open(os.path.join(test_dir, subdir_name2, subdir_name3, file_name5), 'w').writelines(['1\n'])

        file_list = get_all_files(test_dir)
        assert len(file_list) == 5

        for ii, fName in enumerate(sorted(file_list)):
            assert os.path.basename(fName) == 'file%s.txt' % (ii + 1)
        shutil.rmtree(test_dir)

    def test_bad_value_checks(self):
        """Test the various "bad value" checks for Inf, NaN, and masked values.
        """

        # Create a test array
        l_x = np.ma.masked_array([0, np.Inf, np.NaN, 0], [False, False, False, True])

        # Test each value with each method
        for i, x in enumerate(l_x):

            # Check with individual methods
            assert is_inf(x) == (i == 1)
            assert is_nan(x) == (i == 2)
            assert is_masked(x) == (i == 3)

            # Check with combo methods
            assert is_inf_or_nan(x) == (is_inf(x) or is_nan(x) and not is_masked(x))
            assert is_nan_or_masked(x) == (is_nan(x) or is_masked(x))
            assert is_inf_nan_or_masked(x) == (is_inf(x) or is_nan(x) or is_masked(x))

            # Check with `any` methods on this individual value
            assert any_is_inf_or_nan(x) == (is_inf(x) or is_nan(x) and not is_masked(x))
            assert any_is_nan_or_masked(x) == (is_nan(x) or is_masked(x))
            assert any_is_inf_nan_or_masked(x) == (is_inf(x) or is_nan(x) or is_masked(x))

        # Test the 'any' methods on full arrays

        assert any_is_inf_or_nan(l_x) == True
        assert any_is_nan_or_masked(l_x) == True
        assert any_is_inf_nan_or_masked(l_x) == True
