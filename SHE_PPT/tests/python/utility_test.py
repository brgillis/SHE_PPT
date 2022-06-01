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

import numpy as np

from SHE_PPT.testing.utility import SheTestCase
from SHE_PPT.utility import (any_is_inf_nan_or_masked, any_is_inf_or_nan, any_is_nan_or_masked, get_all_files,
                             get_nested_attr,
                             is_inf, is_inf_nan_or_masked, is_inf_or_nan,
                             is_masked, is_nan, is_nan_or_masked,
                             process_directory,
                             set_nested_attr, )


class TestUtility(SheTestCase):
    """Class to handle unit tests for functions in the `SHE_PPT.utility` module.
    """

    def test_get_set_nested_attr(self):
        """Unit test of `get/set_nested_attr` functions.
        """

        class DoubleNestedClass(object):

            def __init__(self):
                self.subsubval = "foo"

        class NestedClass(object):

            def __init__(self):
                self.subobj = DoubleNestedClass()
                self.subval = "bar"

        class ContainingClass(object):

            def __init__(self):
                self.obj = NestedClass()
                self.val = "me"

        c = ContainingClass()

        # Check basic get_nested_attr functionality
        assert get_nested_attr(c, "val") == "me"
        assert get_nested_attr(c, "obj.subval") == "bar"
        assert get_nested_attr(c, "obj.subobj.subsubval") == "foo"

        # Check set_nested_attr functionality
        set_nested_attr(c, "val", 15)
        set_nested_attr(c, "obj.subval", "Fif.teen")
        set_nested_attr(c, "obj.subobj.subsubval", (5, "t.e.e.n"))

        assert get_nested_attr(c, "val") == 15
        assert get_nested_attr(c, "obj.subval") == "Fif.teen"
        assert get_nested_attr(c, "obj.subobj.subsubval") == (5, "t.e.e.n")

        return

    def test_process_directory(self):
        """
        """
        test_dir = os.path.join(os.getenv('HOME'), 'fgdyteihth')
        os.mkdir(test_dir)
        subdir_name1 = 'sub_a'
        os.mkdir(os.path.join(test_dir, subdir_name1))
        # subdir_name2='sub_b'
        # os.mkdir(os.path.join(test_dir,subdir_name2))
        file_name1 = 'file1.txt'
        file_name2 = 'file2.txt'
        open(os.path.join(test_dir, file_name1), 'w').writelines(['1\n'])
        open(os.path.join(test_dir, file_name2), 'w').writelines(['2\n'])
        file_list, sbdir_list = process_directory(test_dir)
        assert len(file_list) == 2
        assert len(sbdir_list) == 1
        shutil.rmtree(test_dir)

    def test_get_all_files(self):
        """
        """
        test_dir = os.path.join(os.getenv('HOME'), 'fgdytedggdsth')
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
        """ Test the various "bad value" checks for Inf, NaN, and masked values.
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
