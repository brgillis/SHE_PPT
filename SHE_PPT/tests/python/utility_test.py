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

from EL_PythonUtils.utilities import get_arguments_string, hash_any
from SHE_PPT.utility import (any_is_inf_nan_or_masked, any_is_inf_or_nan, any_is_nan_or_masked, get_all_files,
                             get_nested_attr,
                             is_inf_nan_or_masked, is_inf_or_nan,
                             is_nan_or_masked,
                             process_directory,
                             set_nested_attr, )


class TestUtility:
    """


    """

    @classmethod
    def setup_class(cls):
        return

    @classmethod
    def teardown_class(cls):
        return

    def test_get_set_nested_attr(self):

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

    def test_hash_any(self):

        test_str = "my_string"
        test_obj = ("this_is_my_tuple", 1)

        # Check that maximum length is enforced properly
        max_length = 16
        assert len(hash_any(test_str, max_length = max_length)) == max_length
        assert len(hash_any(test_obj, max_length = max_length)) == max_length
        assert len(hash_any(test_obj, format = "base64", max_length = max_length)) == max_length

        smaller_max_length = 8
        assert hash_any(test_str, max_length = max_length)[
               :max_length - smaller_max_length] == hash_any(test_str, max_length = smaller_max_length)
        assert hash_any(test_obj, max_length = max_length)[
               :max_length - smaller_max_length] == hash_any(test_obj, max_length = smaller_max_length)
        assert (hash_any(test_obj, max_length = max_length, format = "base64")[:max_length - smaller_max_length] ==
                hash_any(test_obj, max_length = smaller_max_length, format = "base64"))

        # Check that base64 encoding is working as expected - should be shorter than hex encoding
        assert len(hash_any(test_str, format = "hex")) > len(hash_any(test_str, format = "base64"))
        assert len(hash_any(test_obj, format = "hex")) > len(hash_any(test_obj, format = "base64"))

    def test_get_arguments_string(self):

        # Set up a mock arguments object
        class TestArgs(object):

            def __init__(self):
                self.foo = "bar"
                self.foobar = ["bar", "foo "]
                return

        test_args = TestArgs()

        # Test with no command string
        arg_string = get_arguments_string(test_args)

        # Have to test both possible orders of arguments since it's indeterminate
        assert ((arg_string == "--foo bar --foobar bar foo") or
                (arg_string == "--foobar bar foo --foo bar"))

        # Test with a command string
        cmd_string = get_arguments_string(test_args, cmd = "run")
        assert ((cmd_string == "run --foo bar --foobar bar foo") or
                (cmd_string == "run --foobar bar foo --foo bar"))

        # Test it strips the command string properly
        cmd_string2 = get_arguments_string(test_args, cmd = "run ")
        assert ((cmd_string2 == "run --foo bar --foobar bar foo") or
                (cmd_string2 == "run --foobar bar foo --foo bar"))

        # Try with store_true/false
        class TestBoolArgs(object):

            def __init__(self):
                self.stt = True
                self.stf = False
                self.sff = False
                self.sft = True
                return

        test_bool_args = TestBoolArgs()
        bool_arg_string = get_arguments_string(test_bool_args, store_true = ["stt", "stf"],
                                               store_false = ["sff", "sft"])
        assert ((bool_arg_string == "--stt --sff") or
                (bool_arg_string == "--sff --stt"))

        # Test if it properly puts quotes around args with spaces in them
        test_space_args = TestArgs()
        test_space_args.foo = "b a r"
        test_space_args.foobar = ["bar", "f o o"]

        space_arg_string = get_arguments_string(test_space_args)
        assert ((space_arg_string == '--foo "b a r" --foobar bar "f o o"') or
                (space_arg_string == '--foobar bar "f o o" --foo "b a r"'))

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
        for x in l_x:

            # Check with combo methods
            assert is_inf_or_nan(x) == (np.isinf(x) or np.isnan(x) and not np.ma.is_masked(x))
            assert is_nan_or_masked(x) == (np.isnan(x) or np.ma.is_masked(x))
            assert is_inf_nan_or_masked(x) == (np.isinf(x) or np.isnan(x) or np.ma.is_masked(x))

            # Check with `any` methods on this individual value
            assert any_is_inf_or_nan(x) == (np.isinf(x) or np.isnan(x))
            assert any_is_nan_or_masked(x) == (np.isnan(x) or np.ma.is_masked(x))
            assert any_is_inf_nan_or_masked(x) == (np.isinf(x) or np.isnan(x) or np.ma.is_masked(x))

        # Test the 'any' methods on full arrays

        assert any_is_inf_or_nan(l_x) == True
        assert any_is_nan_or_masked(l_x) == True
        assert any_is_inf_nan_or_masked(l_x) == True
